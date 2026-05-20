const { MongoClient } = require("mongodb");

let cachedClient;

async function getCollection() {
  if (!process.env.MONGODB_URI) {
    throw new Error("MONGODB_URI is not configured");
  }
  if (!cachedClient) {
    cachedClient = new MongoClient(process.env.MONGODB_URI);
    await cachedClient.connect();
  }
  const dbName = process.env.MONGODB_DB || "tutorspark";
  const collectionName = process.env.MONGODB_COLLECTION || "study_submissions";
  return cachedClient.db(dbName).collection(collectionName);
}

async function readBody(req) {
  if (req.body && typeof req.body === "object") {
    return req.body;
  }
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(Buffer.from(chunk));
  }
  const raw = Buffer.concat(chunks).toString("utf8");
  return raw ? JSON.parse(raw) : {};
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }
  if (req.method !== "POST") {
    res.status(405).json({ ok: false, error: "Method not allowed" });
    return;
  }

  try {
    const payload = await readBody(req);
    const participantCode = String(payload.participantCode || "").trim();
    if (!participantCode) {
      res.status(400).json({ ok: false, error: "participantCode is required" });
      return;
    }

    const collection = await getCollection();
    const submittedAt = new Date();
    const record = {
      ...payload,
      submittedAt,
      source: "vercel",
      requestMeta: {
        userAgent: req.headers["user-agent"] || "",
        ip:
          req.headers["x-forwarded-for"] ||
          req.headers["x-real-ip"] ||
          "",
      },
    };
    const result = await collection.insertOne(record);
    res.status(200).json({
      ok: true,
      id: result.insertedId.toString(),
      submittedAt: submittedAt.toISOString(),
    });
  } catch (error) {
    console.error("submit-study failed", error);
    res.status(500).json({ ok: false, error: "Study submission failed" });
  }
};
