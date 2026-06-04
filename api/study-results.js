const { MongoClient, ObjectId } = require("mongodb");

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

function sanitize(record) {
  return {
    ...record,
    _id: record._id instanceof ObjectId ? record._id.toString() : record._id,
  };
}

function csvEscape(value) {
  const text = value == null ? "" : String(value);
  if (/[",\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

function toCsv(records) {
  const rows = [
    [
      "id",
      "submitted_at",
      "participant_code",
      "hero_name",
      "hero_class",
      "difficulty",
      "quest_title",
      "subject_title",
      "score_correct",
      "score_total",
      "age_range",
      "learning_background",
      "cs_experience",
      "primary_device",
      "open_feedback",
      "frustration_notes",
      "positive_notes",
      "support_actions_used",
      "dojo_opened",
      "coach_nudges",
      "missed_topics",
      "mastery_recommendation",
    ],
  ];
  for (const record of records) {
    const supportUsage = record.supportUsage || {};
    const supportActionsUsed =
      Number(supportUsage.hint || 0) +
      Number(supportUsage.fiftyFifty || 0) +
      Number(supportUsage.friendCall || 0) +
      Number(supportUsage.freePass || 0);
    const missedTopics = record.missedTopics
      ? Object.entries(record.missedTopics).map(([topic, count]) => `${topic} (${count})`).join("; ")
      : "";
    rows.push([
      record._id,
      record.submittedAt,
      record.participantCode,
      record.heroName,
      record.heroClass,
      record.difficultyLabel || record.difficultyKey || "",
      record.questTitle,
      record.subjectTitle,
      record.score && record.score.correct,
      record.score && record.score.total,
      record.demographics && record.demographics.age_range,
      record.demographics && record.demographics.learning_background,
      record.demographics && record.demographics.cs_experience,
      record.demographics && record.demographics.primary_device,
      record.demographics && record.demographics.open_feedback,
      record.demographics && record.demographics.frustration_notes,
      record.demographics && record.demographics.positive_notes,
      supportActionsUsed,
      supportUsage.dojoOpened || 0,
      supportUsage.coachingNudges || 0,
      missedTopics,
      record.masteryRecommendation || "",
    ]);
  }
  return rows.map((row) => row.map(csvEscape).join(",")).join("\n");
}

module.exports = async function handler(req, res) {
  if (!["GET", "DELETE"].includes(req.method)) {
    res.status(405).json({ ok: false, error: "Method not allowed" });
    return;
  }

  const key = req.query.key || req.headers["x-study-admin-key"];
  if (!process.env.STUDY_ADMIN_KEY || key !== process.env.STUDY_ADMIN_KEY) {
    res.status(401).json({ ok: false, error: "Unauthorized" });
    return;
  }

  try {
    const collection = await getCollection();
    if (req.method === "DELETE") {
      if (req.query.confirm !== "DELETE") {
        res.status(400).json({
          ok: false,
          error: "Add confirm=DELETE to clear study submissions",
        });
        return;
      }
      const result = await collection.deleteMany({});
      res.status(200).json({ ok: true, deletedCount: result.deletedCount });
      return;
    }

    const limit = Math.min(Number(req.query.limit || 1000), 5000);
    const records = (await collection.find({}).sort({ submittedAt: -1 }).limit(limit).toArray()).map(sanitize);
    if (req.query.format === "csv") {
      res.setHeader("Content-Type", "text/csv; charset=utf-8");
      res.setHeader("Content-Disposition", "attachment; filename=tutorspark-study-results.csv");
      res.status(200).send(toCsv(records));
      return;
    }
    res.status(200).json({ ok: true, count: records.length, records });
  } catch (error) {
    console.error("study-results failed", error);
    res.status(500).json({ ok: false, error: "Study export failed" });
  }
};
