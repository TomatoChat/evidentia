# Evidentia Frontend

A modern React/Next.js frontend for the Evidentia brand research tool.

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

Create a `.env.local` file with:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Deployment

This frontend is designed to be deployed on Vercel:

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set the environment variable `NEXT_PUBLIC_API_URL` to your backend API URL
4. Deploy!

## Features

- Two-step landing page (email collection → brand analysis)
- Modern UI with Tailwind CSS
- Responsive design
- API integration with Flask backend
- Streaming response support