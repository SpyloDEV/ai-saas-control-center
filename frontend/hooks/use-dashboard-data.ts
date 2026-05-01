import { useQuery } from "@tanstack/react-query";

export function useDashboardData() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => ({
      kpis: [
        { label: "Agents", value: 12, delta: "+3" },
        { label: "Documents", value: 842, delta: "+18%" },
        { label: "Workflows", value: 24, delta: "+5" },
        { label: "Success rate", value: "98.4%", delta: "+1.2%" },
      ],
      activity: [
        "Invoice extraction completed for Northstar AI Labs",
        "Workflow Document Intake finished in 812 ms",
        "API key Backend SDK rotated by owner",
        "Validation Agent flagged missing tax ID",
      ],
    }),
  });
}
