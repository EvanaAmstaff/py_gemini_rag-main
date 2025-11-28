// index.mjs
import "dotenv/config";
import axios from "axios";
import cheerio from "cheerio";
import RSSParser from "rss-parser";
import { Client } from "@notionhq/client";

const notion = new Client({ auth: process.env.NOTION_TOKEN });

const DB_ID = (process.env.DATABASE_ID || process.env.NOTION_DATABASE_ID);
if (!DB_ID) throw new Error("DATABASE_ID is required in env");

const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY || "";
const YOUTUBE_CHANNEL_IDS = (process.env.YOUTUBE_CHANNEL_IDS || "").split(",").map(s => s.trim()).filter(Boolean); // comma separated channels
const TIKTOK_USERS = (process.env.TIKTOK_USERS || "").split(",").map(s => s.trim()).filter(Boolean); // optional
const RSS_FEEDS = (process.env.RSS_FEEDS || "").split(",").map(s => s.trim()).filter(Boolean);

console.log("DATABASE ID:", DB_ID);

// helper: check if URL already exists in DB (very lightweight)
async function findPageByUrl(url) {
  try {
    // Notion new API: query database filtering by url property if exists; fallback: scan recent pages (simple)
    // We'll attempt a search (not perfect), but keep it minimal: query pages and look for matching property values
    const res = await notion.databases.retrieve({ database_id: DB_ID });
    // if properties exist and there is a URL property name, try filtering; otherwise brute-force small scan (costly)
    // We'll just retrieve first 30 pages and check property values (sufficient for small DB)
    const pages = await notion.pages.list? await notion.pages.list({page_size:30}) : { results: [] };
    for (const p of pages.results || []) {
      const props = p.properties || {};
      for (const [k,v] of Object.entries(props)) {
        // url properties shape varies; try common ones
        if (v?.url && v.url === url) return p;
        if (v?.rich_text && v.rich_text[0]?.plain_text === url) return p;
        if (v?.type === "url" && v?.url === url) return p;
      }
    }
  } catch (e) {
    // ignore and proceed (we'll de-duplicate best-effort)
  }
  return null;
}

async function createPageMinimal(title, url, sourceName) {
  try {
    // detect title property key
    const db = await notion.databases.retrieve({ database_id: DB_ID });
    const properties = db.properties || {};
    // find title property key
    const titleKey = Object.keys(properties).find(k => properties[k]?.type === "title") || "Name";

    // find appropriate URL property key (we try to use the provided sourceName property if exists)
    const urlKeyCandidates = [sourceName, "URL", "Link", "リンク", "Url"].map(s=>s).filter(Boolean);
    let urlKey = Object.keys(properties).find(k => ["url","rich_text","text"].includes(properties[k]?.type) && urlKeyCandidates.includes(k));
    if (!urlKey) urlKey = Object.keys(properties).find(k => properties[k]?.type === "url") || Object.keys(properties).find(k => properties[k]?.type === "rich_text") || null;

    // Build properties object
    const props = {};
    props[titleKey] = { title: [{ text: { content: title } }] };
    if (urlKey) {
      if (properties[urlKey]?.type === "url") {
        props[urlKey] = { url };
      } else {
        // store URL in rich_text
        props[urlKey] = { rich_text: [{ text: { content: url } }] };
      }
    } else {
      // No suitable url property, skip adding url to properties
    }

    const created = await notion.pages.create({
      parent: { database_id: DB_ID },
      properties: props
    });
    console.log(`Created page ${created.id} (${sourceName})`);
    return created;
  } catch (err) {
    console.error("Failed to create page:", err?.message || err);
    throw err;
  }
}

/* ========== YouTube ========== */
async function fetchYouTubeLatest() {
  if (!YOUTUBE_API_KEY || YOUTUBE_CHANNEL_IDS.length === 0) {
    console.log("YouTube: API key or channel IDs not set. Skipping.");
    return [];
  }
  const results = [];
  try {
    for (const channelId of YOUTUBE_CHANNEL_IDS) {
      // get uploads playlist id via channels.list
      const chRes = await axios.get('https://www.googleapis.com/youtube/v3/channels', {
        params: { part: 'contentDetails', id: channelId, key: YOUTUBE_API_KEY }
      });
      const items = chRes.data.items || [];
      if (!items.length) continue;
      const uploadsPlaylist = items[0].contentDetails.relatedPlaylists.uploads;
      const pl = await axios.get('https://www.googleapis.com/youtube/v3/playlistItems', {
        params: { part: 'snippet', playlistId: uploadsPlaylist, maxResults: 3, key: YOUTUBE_API_KEY }
      });
      for (const it of pl.data.items || []) {
        const title = it.snippet.title;
        const videoId = it.snippet.resourceId?.videoId;
        if (videoId) {
          const url = `https://www.youtube.com/watch?v=${videoId}`;
          results.push({ title, url, source: "YouTube" });
        }
      }
    }
  } catch (e) {
    console.error("YouTube fetch error:", e?.message || e);
  }
  return results;
}

/* ========== TikTok (simple scraping - fragile) ========== */
async function fetchTikTokLatest() {
  if (TIKTOK_USERS.length === 0) {
    console.log("TikTok: no users defined. Skipping.");
    return [];
  }
  const out = [];
  try {
    for (const user of TIKTOK_USERS) {
      // fetch user's page HTML and parse first video link
      const url = `https://www.tiktok.com/@${encodeURIComponent(user)}`;
      const r = await axios.get(url, { headers: { "User-Agent": "Mozilla/5.0" } , timeout: 15000 });
      const $ = cheerio.load(r.data);
      // search for links to /@user/video/...
      const anchor = $('a[href*="/video/"]').first();
      let link = anchor.attr('href');
      let title = anchor.attr('title') || `${user} - TikTok`;
      if (!link) {
        // fallback: find script with JSON
        const scripts = $('script').toArray();
        for (const s of scripts) {
          const txt = $(s).html() || "";
          const m = txt.match(/"authorName":"([^"]+)"/);
          if (m) { title = m[1]; }
          const mm = txt.match(/"playAddr":"([^"]+)"/);
          if (mm && mm[1]) { link = mm[1].replace(/\\u0026/g, "&"); break; }
        }
      }
      if (link && link.startsWith('/')) link = `https://www.tiktok.com${link}`;
      if (link) out.push({ title, url: link, source: "TikTok" });
    }
  } catch (e) {
    console.error("TikTok fetch error:", e?.message || e);
  }
  return out;
}

/* ========== RSS ========== */
const rssParser = new RSSParser();
async function fetchRSSLatest() {
  if (RSS_FEEDS.length === 0) {
    console.log("RSS: no feeds configured. Skipping.");
    return [];
  }
  const out = [];
  for (const feed of RSS_FEEDS) {
    try {
      const f = await rssParser.parseURL(feed);
      (f.items || []).slice(0,5).forEach(item => {
        out.push({ title: item.title || item.contentSnippet || "RSS item", url: item.link, source: "RSS" });
      });
    } catch (e) {
      console.error("RSS fetch error for", feed, e?.message || e);
    }
  }
  return out;
}

/* ========== Main flow ========== */
async function main() {
  try {
    const yt = await fetchYouTubeLatest();
    const tk = await fetchTikTokLatest();
    const rs = await fetchRSSLatest();
    const all = [...yt, ...tk, ...rs];
    console.log(`Found total ${all.length} items.`);

    for (const item of all) {
      if (!item.url) continue;
      const existing = await findPageByUrl(item.url);
      if (existing) {
        console.log("Already exists, skip:", item.url);
        continue;
      }
      try {
        await createPageMinimal(item.title, item.url, item.source === "YouTube" ? "YouTube" : item.source === "TikTok" ? "TikTok" : "RSS");
      } catch (e) {
        console.error("Failed create:", e?.message || e);
      }
    }
    console.log("Done.");
  } catch (e) {
    console.error("Fatal error:", e);
  }
}

await main();
