import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";

const SYSTEM_PROMPT = `You are a senior digital forensics analyst advising law enforcement investigators at ICMEC.
Write exactly 3 sentences — no more. Be direct and operational. No bullet points, no generic statements.
Every sentence must name a specific tool or action. Stop after the third sentence.`;

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { caseInput, top5Tools } = req.body;

  const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
  const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;
  const region = process.env.AWS_REGION || "us-east-1";
  const modelId = process.env.AWS_MODEL_ID || "mistral.mistral-small-2402-v1:0";

  if (!accessKeyId || !secretAccessKey) {
    return res.status(500).json({ error: "AWS credentials not configured" });
  }

  try {
    const client = new BedrockRuntimeClient({
      region,
      credentials: { accessKeyId, secretAccessKey },
    });

    const { investigationTypes = [], inputs = [], skillLevel, budget, urgency } = caseInput;
    const toolsList = top5Tools
      .map((t, i) => `${i + 1}. ${t.name} [${t.category}] — ${t.description || "No description"}`)
      .join("\n");

    const fullPrompt = `${SYSTEM_PROMPT}

CASE CONTEXT:
- Investigation type(s): ${investigationTypes.join(", ")}
- Evidence available: ${inputs.length > 0 ? inputs.join(", ") : "Not specified"}
- Skill level: ${skillLevel} | Budget: ${budget} | Urgency: ${urgency || "Not specified"}

TOP RECOMMENDED TOOLS:
${toolsList}

Write a 3–4 sentence Case Analysis Brief: explain why these tools collectively address this investigation, suggest a logical workflow order (which to use first, second, etc.), and flag any critical limitation or legal consideration. Write as a coherent analytical paragraph, not a list.`;

    const payload = {
      prompt: `<s>[INST] ${fullPrompt} [/INST]`,
      max_tokens: 180,
      temperature: 0.4,
    };

    const command = new InvokeModelCommand({
      modelId,
      contentType: "application/json",
      accept: "application/json",
      body: JSON.stringify(payload),
    });

    const response = await client.send(command);
    const decoder = new TextDecoder();
    const result = JSON.parse(decoder.decode(response.body));
    const raw = result.outputs?.[0]?.text?.trim() || null;
    // Enforce 3-sentence cap server-side — Mistral doesn't reliably self-limit
    // Split on ". " followed by a capital letter to avoid splitting "ReportBox 2.0" etc.
    const brief = raw
      ? raw.split(/(?<=\.)\s+(?=[A-Z])/).slice(0, 3).join(" ").trim()
      : null;

    res.json({ brief });
  } catch (err) {
    console.error("Bedrock error:", err.message);
    res.status(500).json({ error: "Bedrock call failed", detail: err.message });
  }
}
