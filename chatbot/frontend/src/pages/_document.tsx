import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* OpenAI ChatKit Web Component */}
        <script
          type="module"
          src="https://cdn.jsdelivr.net/npm/@openai/chatkit@latest/dist/chatkit.min.js"
          async
        />

        {/* Preconnect to improve performance */}
        <link rel="preconnect" href="https://cdn.jsdelivr.net" />
        <link rel="dns-prefetch" href="https://cdn.jsdelivr.net" />

        <meta name="description" content="Todo AI Dashboard with ChatKit - Intelligent natural language task management" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
