import requests

description = """
Macro trends blogger and economist David Woo, CEO of David Woo Unbound ‪@DavidWooUnbound‬, joins Julia La Roche on episode 228 in a two-part interview. On Monday, he rejoined to provide analysis on China's DeepSeek AI breakthrough and the massive macro implications. On Friday, he provided a deep dive into Trump's second term strategy and the global chess moves, from US-China negotiations to the crucial role of Mexico in border security.
In Part 1, Woo discusses how DeepSeek's AI model from China has impacted markets, with the NASDAQ down 3% and Nvidia dropping over 16%. He examines how this development challenges US tech monopolies' dominance and what this means for US economic exceptionalism and tech sector valuations.
In Part 2, Woo analyzes the challenges facing Trump's second term, particularly regarding fiscal policy and the extension of the 2017 tax cuts. He highlights the critical role of the Freedom Caucus, which holds significant power with Republicans' one-seat majority in the House. The discussion covers several key areas:
- The potential alliance between the Freedom Caucus and Elon Musk on fiscal policy
- Mexico's proactive approach to border security and trade relations
- Contrasting positions of Mexico and Canada on trade negotiations
- The complexities of the TikTok situation and potential solutions
- US-China relations and the possibility of returning to the Phase One trade agreement
- Investment opportunities in Chinese equities, the Mexican peso, and 5-year US Treasuries
"""

prompt = (
    f"请根据以下视频描述生成一个简洁的标题和摘要。\n\n"
    f"原始描述：\n{description}\n\n"
    "要求：\n"
    "1. 标题应简洁明了，突出视频的主要内容和关键人物；\n"
    "2. 摘要应保留描述中的核心信息，去除冗余内容；\n"
    "3. 使用专业、清晰的语言；\n"
    "4. 输出格式：\n"
    "标题：xxx\n"
    "摘要：xxx\n"
)

response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1:70b-llama-distill-q4_K_M",
                "prompt": prompt,
                "stream": False
            }
        )