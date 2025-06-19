"""AI prompts for blog post generation."""

STYLE_ANALYSIS_PROMPT = """
Analyze the following blog posts to understand Priyanshu Jain's writing style:

CHARACTERISTICS TO EXTRACT:
- Tone and voice (personal, professional, reflective, etc.)
- Sentence structure patterns
- Paragraph length and flow
- How he transitions between topics
- Use of technical vs. simple language
- Personal anecdotes and experiences
- Way of connecting personal experiences to broader insights

BLOG POSTS:
{existing_posts}

Based on this analysis, describe his writing style in detail.
"""

BLOG_CONVERSION_PROMPT = """
You are a content editor for Priyanshu Jain's personal blog. Convert the following raw notes into his distinctive writing style for a blog post.

PRIYANSHU'S WRITING STYLE:
- Personal, reflective tone that connects experiences to broader insights
- Exactly two focused paragraphs
- Clear, direct language that makes technical concepts accessible
- Weaves personal experiences into universal themes
- Conversational but thoughtful
- Uses specific examples and anecdotes
- Maintains authenticity and genuine voice

REQUIREMENTS:
1. Create exactly TWO paragraphs
2. Extract a compelling title from the content
3. Maintain his personal, reflective voice
4. Connect personal experiences to broader insights
5. Keep it concise but meaningful
6. Ensure it flows naturally

RAW NOTES:
{notes}

EXISTING BLOG POSTS FOR STYLE REFERENCE:
{style_examples}

Return the response in this exact JSON format:
{{
    "title": "Blog Post Title",
    "content": "First paragraph text.\\n\\nSecond paragraph text.",
    "date": "YYYY-MM-DD"
}}

IMPORTANT: The content should be exactly two paragraphs separated by \\n\\n. Make sure the writing matches Priyanshu's authentic voice and style.
"""

TITLE_EXTRACTION_PROMPT = """
Extract a compelling blog post title from the following content. The title should:
- Be concise (3-8 words)
- Capture the main theme or insight
- Match Priyanshu's blog style (look at existing titles for reference)
- Be engaging but not clickbait-y

CONTENT:
{content}

EXISTING TITLES FOR REFERENCE:
- "Reflecting on 2024"
- "How I Code with AI" 
- "Philosophy of RPC"
- "Developers Hate JIRA"
- "Imagining the Ideal Software"
- "T-shaped engineer"
- "Level of error handling"
- "Software bugs"
- "Why software projects are notoriously late?"
- "Does altruism really exist?"
- "Naming is hard"
- "Why Chrome?"

Return only the title, nothing else.
"""

def get_style_examples() -> str:
    """Get example blog posts for style reference."""
    return """
EXAMPLE 1 - "Reflecting on 2024":
New years get people in a reflective mood, and I wanted to share some personal thoughts about how it has gone so far, and some of the things I've done and learned along the way.

I welcomed 2024 amidst the serene beauty of the mountains, a setting that profoundly influenced me. That trip inspired me to sign up for a long-dreamed mountaineering course at HMI (Himalayan Mountaineering Institute) in Darjeeling. Later in the year, I completed the course, diving deep into the technicalities of mountaineering, rock climbing, practicing on the Rathong Glacier, and even climbing the 5,000m Mount Renok. It was a transformative experience that taught me resilience, teamwork, and the sheer joy of pushing physical and mental boundaries.

EXAMPLE 2 - "T-shaped engineer":
The concept of a T-shaped engineer has become increasingly relevant in today's fast-evolving tech landscape. Unlike specialists who dive deep into one area (the I-shaped engineer) or generalists who know a little about everything (the dash-shaped engineer), T-shaped engineers combine deep expertise in one domain with broad knowledge across multiple areas. This combination allows them to collaborate effectively across teams while bringing specialized skills to complex problems.

What makes T-shaped engineers particularly valuable is their ability to bridge gaps between different technical domains and business requirements. They can communicate technical concepts to non-technical stakeholders, understand the broader system implications of their specialized work, and adapt to new technologies and methodologies. In my experience building systems across different domains, this breadth of knowledge often proves as crucial as deep technical expertise—it's what enables you to see the bigger picture and make decisions that benefit the entire system rather than just optimizing for one component.
"""