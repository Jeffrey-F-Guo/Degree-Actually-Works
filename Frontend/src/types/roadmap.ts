export type NodeStatus = 'not-started' | 'in-progress' | 'completed' | 'skipped';

export interface CourseNode {
  id: string;
  code: string;
  title: string;
  type: 'core' | 'elective';
  prereqs: string[];
  tags: string[];
  description?: string;
  whyMatters?: string;
}

export interface NodeGroup {
  title: string;
  nodes: CourseNode[];
}

export interface RoadmapPath {
  slug: string;
  name: string;
  goal: string;
  summary: string;
  coreEmphasis: string[];
  groups: NodeGroup[];
  wwuLinks: string[];
}

export interface PathsData {
  paths: RoadmapPath[];
}

export interface UserProgress {
  [nodeId: string]: {
    status: NodeStatus;
    updatedAt: string;
  };
}

export interface ShareableState {
  pathSlug: string;
  progress: Record<string, NodeStatus>;
}

export interface GraphNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: CourseNode & {
    status: NodeStatus;
    onClick: (nodeId: string) => void;
  };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: 'smoothstep';
  animated?: boolean;
}