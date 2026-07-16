CAREER_ANALYZER_PROMPT = """
You are an expert web scraping architect.

You are given the HTML of a company's career page.

Analyze the page and determine:

1. Company Name
2. ATS Platform
   Examples:
   - Greenhouse
   - Lever
   - Ashby
   - Workday
   - SmartRecruiters
   - Oracle
   - SAP
   - Custom

3. Are job listings embedded directly in the HTML?

4. Does the page contain links to individual job pages?

5. Does it contain Apply links?

6. Does it appear that JavaScript loads jobs dynamically?

7. Is pagination used?

8. Are there signs of API-based loading?

9. Recommend the best extraction strategy.

Return ONLY valid JSON.

HTML:

{html}
"""