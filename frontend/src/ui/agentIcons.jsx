import { BookOpen, Users, Briefcase, MessageSquare, Target } from "lucide-react";

const ICONS = {
  skill_building: BookOpen,
  networking: Users,
  portfolio: Briefcase,
  interview_prep: MessageSquare,
};

export function AgentIcon({ agent, size = 14 }) {
  const Icon = ICONS[agent] || Target;
  return <Icon size={size} aria-hidden="true" />;
}