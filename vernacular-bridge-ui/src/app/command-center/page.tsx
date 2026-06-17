import CommandCenterLayout from "@/components/command-center/CommandCenterLayout";

export const metadata = {
  title: "Command Center | Vernacular Bridge",
  description: "Independent AI Learning & Coaching Control Center",
};

export default function Page() {
  return (
    <main className="h-screen overflow-hidden bg-slate-50">
      <CommandCenterLayout />
    </main>
  );
}
