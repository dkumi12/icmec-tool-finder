import "dotenv/config";
import express from "express";
import handler from "./api/explain.js";

const app = express();
app.use(express.json());

app.post("/api/explain", handler);

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`[API] Local Bedrock proxy running on http://localhost:${PORT}`);
});
