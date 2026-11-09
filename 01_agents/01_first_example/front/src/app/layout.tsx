import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cadastro | Pessoas e celulares",
  description: "Gerencie pessoas e celulares em um só lugar.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
