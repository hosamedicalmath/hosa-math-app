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

// COMPLETELY UPGRADED PROMPT for longer, deeper questions, hidden formulas, and implicit rounding
const SYSTEM_PROMPT = `You are an expert HOSA Medical Math exam writer. Your job is to generate EXTREMELY HARD, long, paragraph-length clinical word problems.

CRITICAL QUESTION DESIGN RULES:
1. COMPLEXITY: Questions MUST be 3 to 4 steps long. (e.g., A patient's weight must be converted, then used to find a daily dose, then divided into doses per shift, then used to calculate an IV drip rate or completion time). 
2. NO FORMULA NAMES: NEVER tell the student what formula to use. DO NOT say "Using the BSA formula" or "calculate the standard deviation." Describe the clinical need and let the student figure out what math/formula to apply.
3. ROUNDING INSTRUCTIONS: HOSA defaults to nearest whole number. Therefore, NEVER explicitly write "round to the nearest whole number" in your question text. It is implied. ONLY mention rounding in the prompt IF you specifically want them to round to the nearest tenth, hundredth, or thousandth.
4. PEDS DOSAGE: ALWAYS round pediatric dosages DOWN to avoid overdose (e.g., 31.9 -> 31).
5. DEFAULT ROUNDING: In your own mathematical answer, if no specific rounding was requested, round the final answer to the nearest whole number.
6. ZEROES: Decimals <1 MUST have a leading zero (0.5). Whole numbers NEVER have a trailing zero (5, not 5.0).
7. NO DOUBLE QUOTES: NEVER use the (") symbol anywhere in your text. Use single quotes ('). NEVER use (") for inches; spell it out (e.g., '5 feet 2 inches').
8. CONVERSIONS TO USE: 1kg=2.2lbs, 1in=2.54cm, 1tsp=5mL, 1tbsp=15mL, 1oz=30mL, 1cup=240mL, 1mL=15gtts. 

Output ONLY valid JSON in this exact format:
{
  "questions": [
    {
      "question": "The long, multi-step clinical word problem text here...",
      "explanation": "Brief step-by-step math showing how to get the answer...",
      "final_answer": "Final number here"
    }
  ]
}`;

app.post('/api/generate', async (req, res) => {
    const { category, count, description } = req.body;
    
    // Auto-Batcher to prevent JSON cutoffs
    const BATCH_SIZE = 4;
    let allGeneratedQuestions = [];
    let remaining = count;
    let attempts = 0;

    try {
        console.log(`\n--- Starting Generation for ${category} (${count} total Qs) ---`);

        while (remaining > 0 && attempts < 15) {
            attempts++;
            const currentBatchCount = Math.min(remaining, BATCH_SIZE);
            console.log(`Requesting batch of ${currentBatchCount} Qs... (${remaining} left to go)`);

            const completion = await groq.chat.completions.create({
                model: "qwen/qwen3-32b",
                messages: [
                    { role: "system", content: SYSTEM_PROMPT },
                    { role: "user", content: `Generate ${currentBatchCount} extremely difficult, paragraph-long clinical questions for: "${category}" (${description}). Output ONLY JSON.` }
                ],
                temperature: 0.25, // Slightly increased to allow more creative/varied clinical scenarios
                max_tokens: 4000
            });

            const rawText = completion.choices[0]?.message?.content || "{}";
            
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
                    console.log(`⚠️ AI formatting mistake. Retrying...`);
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
