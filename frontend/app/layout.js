import "./globals.css";

export const metadata = {
  title: "Mail Hunt — Send internship emails in one go",
  description: "Paste recruiter emails, attach your resume, send individually through Gmail.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
