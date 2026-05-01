"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const schema = z.object({
  name: z.string().min(2),
  role: z.string().min(2),
  model_name: z.string().min(2),
});

type AgentValues = z.infer<typeof schema>;

export function AgentForm() {
  const form = useForm<AgentValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "Revenue QA Agent",
      role: "validation_agent",
      model_name: "mock-control-v1",
    },
  });

  function onSubmit(values: AgentValues) {
    toast.success(`${values.name} queued for creation`);
  }

  return (
    <form
      className="grid gap-3 rounded-lg border bg-card p-4 md:grid-cols-[1fr_1fr_1fr_auto]"
      onSubmit={form.handleSubmit(onSubmit)}
    >
      <Input aria-label="Agent name" {...form.register("name")} />
      <Input aria-label="Agent role" {...form.register("role")} />
      <Input aria-label="Model name" {...form.register("model_name")} />
      <Button type="submit">
        <Plus className="h-4 w-4" />
        Add
      </Button>
    </form>
  );
}
