# AI-Powered Software Engineering Meeting Assistant

An AI-powered meeting assistant specifically designed for software engineering teams to capture, analyze, and extract insights from technical discussions.

## Features

- **Speech Recognition**: Accurate transcription of technical discussions with support for specialized terminology
- **AI Summarization**: Generate structured meeting summaries with key decisions, action items, and technical insights
- **Multi-language Support**: Available in English (US/UK), Spanish, French, German, and Japanese

## Tech Stack

- **Frontend**: React, TypeScript, Tailwind CSS, Radix UI
- **Backend**: TypeScript
- **Database**: SQLAlchemy
- **AI Integration**: OpenAI GPT-4 for summarization and analysis

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Set up your environment variables in the Secrets tab:
- `OPENAI_API_KEY`: Your OpenAI API key

3. Start the development server:
```bash
npm run dev
```

The application will be available at port 5000.

## Project Structure

```
├── client/          # Frontend React application
├── server/          # Express.js backend
│   ├── lib/         # Utility functions and services
│   └── routes/      # API routes
└── shared/          # Shared types and schemas
```

## Features in Detail

### Speech Recognition
- Real-time transcription of meetings
- Support for technical terminology
- Multiple language support

### Visual Content Analysis
- Process technical diagrams
- Analyze code screenshots
- Extract information from whiteboard images

### AI Summarization
- Generate structured meeting summaries
- Extract key decisions and action items
- Identify technical insights and recommendations

## License

MIT
