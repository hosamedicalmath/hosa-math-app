import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import Groq from 'groq-sdk';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const groq = new Groq({
    apiKey: process.env.GROQ_API_KEY
});

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use(express.static(path.join(__dirname, 'public')));

// ADDED RULE: Explicitly ban the " symbol for inches so it stops breaking the JSON
const SYSTEM_PROMPT = `You are a HOSA Medical Math exam writer. Generate EXTREMELY HARD, deep, multi-step word problems.
RULES:
1. ROUNDING: Convert before rounding. Round ONLY the final answer. 
2. Rounding decimals: Look to immediate right. >=5 round up, <=4 round down.
3. DEFAULT: Nearest WHOLE NUMBER unless specified.
4. PEDS DOSAGE: ALWAYS round DOWN to avoid overdose (e.g., 31.9 -> 31).
5. ZEROES: <1 MUST have leading zero (0.5). Whole numbers NEVER have trailing zero (5, not 5.0).
6. CONVERSIONS: 1kg=2.2lbs, 1in=2.54cm, 1tsp=5mL, 1tbsp=15mL, 1oz=30mL, 1cup=240mL, 1mL=15gtts.
7. CRITICAL: DO NOT use double quotes (") anywhere inside your text. Use single quotes (').
8. CRITICAL: NEVER use the " symbol for inches (e.g., 5'2"). You MUST spell it out (e.g., '5 feet 2 inches').

Output ONLY valid JSON in this exact format:
{
  "questions": [
    {
      "question": "Multi-step word problem text here...",
      "explanation": "Brief math steps here...",
      "final_answer": "Final number here"
    }
  ]
}`;

app.post('/api/generate', async (req, res) => {
    const { category, count, description } = req.body;
    
    // We will ask the AI for max 4 questions at a time to prevent JSON cutoffs
    const BATCH_SIZE = 4;
    let allGeneratedQuestions = [];
    let remaining = count;
    let attempts = 0;

    try {
        console.log(`\n--- Starting Generation for ${category} (${count} total Qs) ---`);

        // Loop until we have generated the required number of questions
        while (remaining > 0 && attempts < 15) {
            attempts++;
            const currentBatchCount = Math.min(remaining, BATCH_SIZE);
            console.log(`Requesting batch of ${currentBatchCount} Qs... (${remaining} left to go)`);

            const completion = await groq.chat.completions.create({
                model: "qwen/qwen3-32b",
                messages: [
                    { role: "system", content: SYSTEM_PROMPT },
                    { role: "user", content: `Generate ${currentBatchCount} extremely difficult, multi-step questions for: "${category}" (${description}). Output ONLY JSON.` }
                ],
                temperature: 0.2,
                max_tokens: 4000 // Ensure it has plenty of space to finish the text
            });

            const rawText = completion.choices[0]?.message?.content || "{}";
            
            // Extract the JSON block
            const jsonMatch = rawText.match(/\{[\s\S]*\}/);
            
            if (jsonMatch) {
                try {
                    const batchData = JSON.parse(jsonMatch[0]);
                    if (batchData.questions && Array.isArray(batchData.questions)) {
                        allGeneratedQuestions = allGeneratedQuestions.concat(batchData.questions);
                        remaining -= currentBatchCount;
                        console.log(`✅ Batch successful!`);
                    }
                } catch (parseError) {
                    console.log(`⚠️ AI made a formatting mistake in this batch. Retrying...`);
                    // It will loop again without subtracting from 'remaining'
                }
            } else {
                 console.log(`⚠️ AI failed to return JSON. Retrying...`);
            }
        }

        if (allGeneratedQuestions.length === 0) {
            throw new Error("Failed to generate valid questions after multiple attempts.");
        }

        console.log(`🎉 Successfully finished ${category}! Sent ${allGeneratedQuestions.length} Qs to frontend.`);
        res.json({ questions: allGeneratedQuestions });
        
    } catch (error) {
        console.error(`\n❌ Fatal API Error for ${category}:`);
        console.error(error.message || error);
        res.status(500).json({ error: error.message || "Failed to generate questions." });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
