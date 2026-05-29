DAYS = [
    {
        "day": 1,
        "title": "HTML + Internet Basics",
        "tag": "HTML",
        "xp": 10,
        "items": [
            "HTML creates the page structure",
            "Browser, domain, hosting and server basics",
            "Create index.html for LocalBiz Connect",
            "Open the first page in browser"
        ],
        "task": "Create the first LocalBiz Connect HTML page with header, hero, services and contact section.",
        "default_notes": '''# Day 1 - HTML + Internet Basics

## Topic
HTML, website structure, browser, internet, domain, hosting, URL, request/response.

## Simple Theory
- What is a website?
- What is frontend?
- What is backend?
- What is a browser?
- What happens when we type a website URL?
- Difference between static and dynamic website.
- Basic HTML tags.

## Trainer Demo
Create a simple `index.html` page for **LocalBiz Connect**.

Sections:
- Header
- Hero section
- About section
- Services section
- Contact section
- Footer

## Student Practical
Students create their first HTML page.

## Daily Assignment
Create `student-profile.html` with name, college, skills, career goal and contact section.

## Deliverable
One working HTML page opened in browser.
'''
    },
    {
        "day": 2,
        "title": "CSS + More HTML Pages",
        "tag": "CSS",
        "xp": 10,
        "items": [
            "CSS styles the page",
            "Class, ID, margin, padding and box model",
            "Create style.css",
            "Create dashboard.html"
        ],
        "task": "Style the LocalBiz Connect website and create dashboard page.",
        "default_notes": '''# Day 2 - CSS + More HTML Pages

## Topic
CSS, layout, colors, fonts, cards, buttons, navigation and multiple pages.

## Simple Theory
- What is CSS?
- Inline CSS, internal CSS, external CSS
- Class and ID
- Box model
- Flexbox basics
- Responsive idea

## Trainer Demo
Convert Day 1 HTML into a clean website.

Files:
- style.css
- about.html
- services.html
- contact.html
- dashboard.html

## Daily Assignment
Create service cards for Website Design, App Development, Digital Marketing and IT Support.

## Deliverable
A clean multi-page static website.
'''
    },
    {
        "day": 3,
        "title": "Simple JavaScript + CMD",
        "tag": "JS",
        "xp": 10,
        "items": [
            "JavaScript makes page interactive",
            "Variables, functions and events",
            "DOM and form validation",
            "Useful CMD commands"
        ],
        "task": "Add form validation and a small price calculator.",
        "default_notes": '''# Day 3 - Simple JavaScript + CMD

## Topic
JavaScript basics and Windows CMD.

## Simple Theory
- What is JavaScript?
- Variables
- Functions
- Events
- DOM
- Form validation
- CMD basics

## CMD Commands
`cd`, `dir`, `mkdir`, `cls`, `code .`, `python --version`, `pip --version`, `git --version`

## Trainer Demo
Add JavaScript to contact form:
- Check empty name
- Check valid mobile
- Check valid email
- Show success message
- Change button text after submit

## Daily Assignment
Create a price calculator using JavaScript.

## Deliverable
Interactive frontend website.
'''
    },
    {
        "day": 4,
        "title": "Git and GitHub",
        "tag": "GIT",
        "xp": 10,
        "items": [
            "Understand version control",
            "Create GitHub repository",
            "Commit project files",
            "Push code to GitHub"
        ],
        "task": "Upload the project to GitHub and make 3 commits.",
        "default_notes": '''# Day 4 - Git and GitHub

## Topic
Version control and project upload.

## Simple Theory
- Why developers use Git
- What is repository?
- What is commit?
- What is push?
- What is GitHub?
- Local code vs remote code

## Commands
```bash
git init
git status
git add .
git commit -m "Initial website"
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

## Daily Assignment
Make 3 commits:
1. Added home page
2. Added contact form
3. Added CSS styling

## Deliverable
GitHub repository link.
'''
    },
    {
        "day": 5,
        "title": "Python Flask Web Basics",
        "tag": "FLASK",
        "xp": 10,
        "items": [
            "Understand backend",
            "Create Flask app",
            "Create routes",
            "Render HTML templates"
        ],
        "task": "Run the LocalBiz Connect website from Flask.",
        "default_notes": '''# Day 5 - Python Flask Web Basics

## Topic
Backend basics using Flask.

## Simple Theory
- What is backend?
- What is server?
- What is route?
- What is HTTP GET and POST?
- What is template rendering?
- What is API?

## Trainer Demo
Create:
- app.py
- templates/
- static/

## Daily Assignment
Create routes for `/`, `/about`, `/services`, `/contact`.

## Deliverable
Website running from Flask.
'''
    },
    {
        "day": 6,
        "title": "SQLite, CRUD and API Connection",
        "tag": "DB",
        "xp": 10,
        "items": [
            "Database stores data",
            "Table, row and column",
            "CRUD basics",
            "Frontend form saves to backend"
        ],
        "task": "Save enquiry form data into SQLite and show in admin page.",
        "default_notes": '''# Day 6 - Database, SQLite, CRUD and Frontend-Backend Connection

## Topic
Database, table, insert, select, delete and API connection.

## Simple Theory
- What is a database?
- What is a table?
- What is a row?
- What is a column?
- What is CRUD?
- How frontend sends data to backend

## Trainer Demo
Create SQLite database and enquiry table.

## Daily Assignment
Add delete button for each enquiry.

## Deliverable
Simple working mini app with database.
'''
    },
    {
        "day": 7,
        "title": "AI, ML and GenAI Simple Understanding",
        "tag": "AI",
        "xp": 10,
        "items": [
            "AI, ML and GenAI difference",
            "Dataset and model idea",
            "Small Python AI example",
            "One-page notes"
        ],
        "task": "Create a simple Python prediction example and AI/ML notes.",
        "default_notes": '''# Day 7 - AI, ML and GenAI Simple Understanding

## Topic
AI, ML, Deep Learning, GenAI, model, training and dataset.

## Simple Meaning
- AI: Computer doing intelligent tasks
- ML: Computer learning from data
- GenAI: AI that generates text, image, code or audio
- Model: Trained brain of AI
- Dataset: Data used for training
- Prompt: Instruction given to AI

## Practical Example
Use a simple Python example:
Input: hours practiced
Output: Beginner / Improving / Good

## Important
Training a huge GenAI model from scratch is expensive. In this internship, we understand the idea using small examples.

## Deliverable
AI concept notes + small Python demo.
'''
    },
    {
        "day": 8,
        "title": "AI Prompting",
        "tag": "PROMPT",
        "xp": 10,
        "items": [
            "Bad prompt vs good prompt",
            "Prompt format",
            "Use AI safely",
            "Create AI_PROMPTS.md"
        ],
        "task": "Create a prompt library with 10 useful prompts.",
        "default_notes": '''# Day 8 - AI Prompting

## Topic
How to use AI properly for coding, content, debugging and learning.

## Prompt Format
- Role
- Task
- Context
- Output format
- Rules
- Example

## Student Rules
- Understand before copying
- Ask AI to explain code
- Use only needed part
- Do not paste private data

## Daily Assignment
Create `AI_PROMPTS.md` with 10 useful prompts.

## Deliverable
Prompt library.
'''
    },
    {
        "day": 9,
        "title": "Free AI Tools for Different Uses",
        "tag": "TOOLS",
        "xp": 10,
        "items": [
            "AI tools for coding",
            "AI tools for design",
            "AI tools for writing",
            "Create poster and captions"
        ],
        "task": "Create a brand kit, poster idea and social media captions.",
        "default_notes": '''# Day 9 - Free AI Tools for Different Uses

## Topic
AI tools for coding, design, writing, marketing, video, research and productivity.

## Practical Work
Each student creates:
- One poster in Canva
- One AI-generated project description
- One improved website section using AI
- One social media caption

## Daily Assignment
Prepare:
- Logo idea
- Color palette
- Font suggestion
- 3 social media captions
- 1 poster

## Deliverable
AI tools list + poster.
'''
    },
    {
        "day": 10,
        "title": "Ollama Local AI Model Use",
        "tag": "OLLAMA",
        "xp": 10,
        "items": [
            "Cloud AI vs local AI",
            "Run Ollama model",
            "Prompt local model",
            "Create FAQ dataset"
        ],
        "task": "Create a LocalBiz Connect FAQ bot concept.",
        "default_notes": '''# Day 10 - Ollama Local AI Model Use

## Topic
Running AI locally.

## Simple Theory
- Cloud AI vs local AI
- What is Ollama?
- What is local LLM?
- Why local AI is useful
- Limitations of local AI

## Trainer Demo
```bash
ollama --version
ollama pull llama3.2
ollama run llama3.2
```

## Daily Assignment
Students create 20 FAQ questions and answers.

## Deliverable
Local AI demo + FAQ dataset.
'''
    },
    {
        "day": 11,
        "title": "YOLO Object Detection in Colab",
        "tag": "YOLO",
        "xp": 10,
        "items": [
            "Computer vision basics",
            "What is object detection?",
            "Run YOLO in Colab",
            "Submit screenshot"
        ],
        "task": "Run a pretrained YOLO model in Google Colab.",
        "default_notes": '''# Day 11 - Object Detection with YOLO in Google Colab

## Topic
Computer vision and object detection.

## Simple Theory
- What is computer vision?
- What is image classification?
- What is object detection?
- What is YOLO?
- What is training?
- What is inference?

## Practical
Use a pretrained YOLO model in Google Colab.

## Daily Assignment
Submit:
- Colab notebook link
- Screenshot of detection output
- 5-line explanation

## Deliverable
YOLO Colab demo.
'''
    },
    {
        "day": 12,
        "title": "Resume Building + GitHub Portfolio",
        "tag": "RESUME",
        "xp": 10,
        "items": [
            "Project description",
            "GitHub README",
            "Skills section",
            "LinkedIn post"
        ],
        "task": "Prepare resume project entry and GitHub README.",
        "default_notes": '''# Day 12 - Resume Building + GitHub Portfolio

## Topic
How to present internship work professionally.

## Practical
Create:
- README.md
- resume-project-description.txt
- linkedin-post.txt

## Skills
HTML, CSS, JavaScript, Python, Flask, SQLite, API basics, Git, GitHub, AI Prompting, Ollama, YOLO, Google Colab, WordPress, Canva.

## Deliverable
Resume-ready project documentation.
'''
    },
    {
        "day": 13,
        "title": "WordPress and Digital Marketing",
        "tag": "WP",
        "xp": 10,
        "items": [
            "WordPress basics",
            "Create website pages",
            "SEO title and meta description",
            "Social media captions"
        ],
        "task": "Prepare WordPress content and digital marketing captions.",
        "default_notes": '''# Day 13 - WordPress and Digital Marketing

## Topic
WordPress website creation, landing page, SEO basics and social media posting.

## Student Practical
Create a free WordPress site with:
- Home
- Services
- About
- Contact
- Blog post

## Digital Marketing Practical
Create:
- Instagram caption
- Facebook caption
- SEO title
- Meta description
- Hashtag set

## Deliverable
WordPress link + digital marketing content.
'''
    },
    {
        "day": 14,
        "title": "Final Work Submission and Presentation",
        "tag": "FINAL",
        "xp": 10,
        "items": [
            "Finish project",
            "Submit links/files",
            "Final checklist",
            "Student presentation"
        ],
        "task": "Submit final project and present for 5-8 minutes.",
        "default_notes": '''# Day 14 - Final Work Submission and Presentation

## Topic
Final completion, review, demo and certificate-ready evaluation.

## Final Checklist
- Frontend complete
- Flask routes working
- Database working
- Admin page working
- GitHub updated
- README added
- AI prompt file added
- Poster added
- WordPress link added
- YOLO screenshot added
- Resume text added

## Presentation Format
- Name and college
- Project title
- Problem solved
- Technologies used
- Website demo
- Backend/database demo
- GitHub explanation
- AI tools used
- What they learned

## Deliverable
Final project submission and presentation.
'''
    }
]

def get_day(day_no: int):
    for day in DAYS:
        if day["day"] == day_no:
            return day
    return None
