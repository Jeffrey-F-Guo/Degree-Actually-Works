import { useMemo } from 'react';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  CheckCircle, 
  Clock, 
  Circle, 
  XCircle, 
  ExternalLink,
  BookOpen,
  Target,
  Calendar,
  ArrowRight,
} from 'lucide-react';
import { useRoadmapStore } from '@/store/roadmapStore';
import { RoadmapPath, NodeStatus, CourseNode } from '@/types/roadmap';
import { cn } from '@/lib/utils';

interface NodeDrawerProps {
  path: RoadmapPath;
}

const statusIcons = {
  'not-started': Circle,
  'in-progress': Clock,
  'completed': CheckCircle,
  'skipped': XCircle,
};

const statusLabels = {
  'not-started': 'Not Started',
  'in-progress': 'In Progress',
  'completed': 'Completed',
  'skipped': 'Skipped',
};

const statusColors = {
  'not-started': 'text-muted-foreground',
  'in-progress': 'text-warning',
  'completed': 'text-success',
  'skipped': 'text-muted-foreground',
};

const allStatuses: NodeStatus[] = ['not-started', 'in-progress', 'completed', 'skipped'];

export const NodeDrawer = ({ path }: NodeDrawerProps) => {
  const {
    selectedNodeId,
    isNodeDrawerOpen,
    setNodeDrawerOpen,
    getNodeStatus,
    setNodeStatus,
  } = useRoadmapStore();

  const selectedNode = useMemo(() => {
    if (!selectedNodeId) return null;
    
    for (const group of path.groups) {
      const node = group.nodes.find(n => n.id === selectedNodeId);
      if (node) return node;
    }
    return null;
  }, [selectedNodeId, path]);

  const nodeStatus = selectedNode ? getNodeStatus(path.slug, selectedNode.id) : 'not-started';

  const prerequisites = useMemo(() => {
    if (!selectedNode) return [];
    
    return selectedNode.prereqs.map(prereqId => {
      for (const group of path.groups) {
        const prereq = group.nodes.find(n => n.id === prereqId);
        if (prereq) return prereq;
      }
      return null;
    }).filter(Boolean) as CourseNode[];
  }, [selectedNode, path]);

  const dependents = useMemo(() => {
    if (!selectedNode) return [];
    
    const dependentNodes: CourseNode[] = [];
    for (const group of path.groups) {
      for (const node of group.nodes) {
        if (node.prereqs.includes(selectedNode.id)) {
          dependentNodes.push(node);
        }
      }
    }
    return dependentNodes;
  }, [selectedNode, path]);

  const getRecommendedTiming = (node: CourseNode) => {
    if (prerequisites.length === 0) {
      return "Can be taken early in your program";
    }
    if (prerequisites.length === 1) {
      return `Recommended after completing ${prerequisites[0].title}`;
    }
    return `Recommended after completing prerequisites`;
  };

  if (!selectedNode) return null;

  return (
    <Sheet open={isNodeDrawerOpen} onOpenChange={setNodeDrawerOpen}>
      <SheetContent className="w-[400px] sm:w-[540px] overflow-y-auto custom-scrollbar">
        <SheetHeader className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Badge 
                  variant={selectedNode.type === 'core' ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {selectedNode.type === 'core' ? 'Core Course' : 'Elective'}
                </Badge>
                <div className="text-sm text-muted-foreground font-mono">
                  {selectedNode.code}
                </div>
              </div>
              <SheetTitle className="text-xl">{selectedNode.title}</SheetTitle>
            </div>
          </div>

          {/* Status Selection */}
          <div className="space-y-3">
            <div className="text-sm font-medium">Progress Status</div>
            <div className="grid grid-cols-2 gap-2">
              {allStatuses.map((status) => {
                const StatusIcon = statusIcons[status];
                const isSelected = nodeStatus === status;
                
                return (
                  <Button
                    key={status}
                    variant={isSelected ? "default" : "outline"}
                    size="sm"
                    onClick={() => setNodeStatus(path.slug, selectedNode.id, status)}
                    className={cn(
                      "justify-start gap-2",
                      isSelected && "bg-primary hover:bg-primary/90"
                    )}
                  >
                    <StatusIcon className={cn(
                      "w-4 h-4",
                      isSelected ? "text-primary-foreground" : statusColors[status]
                    )} />
                    <span className="text-xs">{statusLabels[status]}</span>
                  </Button>
                );
              })}
            </div>
          </div>
        </SheetHeader>

        <div className="space-y-6 mt-6">
          {/* Description */}
          {selectedNode.description && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm font-medium">
                <BookOpen className="w-4 h-4" />
                What you'll learn
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {selectedNode.description}
              </p>
            </div>
          )}

          {/* Why it matters */}
          {selectedNode.whyMatters && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Target className="w-4 h-4" />
                Why it matters for {path.name}
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {selectedNode.whyMatters}
              </p>
            </div>
          )}

          {/* Recommended Timing */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Calendar className="w-4 h-4" />
              Recommended Timing
            </div>
            <p className="text-sm text-muted-foreground">
              {getRecommendedTiming(selectedNode)}
            </p>
          </div>

          {/* Prerequisites */}
          {prerequisites.length > 0 && (
            <div className="space-y-3">
              <div className="text-sm font-medium">Prerequisites</div>
              <div className="space-y-2">
                {prerequisites.map((prereq) => {
                  const prereqStatus = getNodeStatus(path.slug, prereq.id);
                  const PrereqStatusIcon = statusIcons[prereqStatus];
                  
                  return (
                    <div 
                      key={prereq.id}
                      className="flex items-center gap-3 p-2 rounded-lg border border-border cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => {
                        setNodeDrawerOpen(false);
                        setTimeout(() => {
                          useRoadmapStore.getState().setSelectedNode(prereq.id);
                          useRoadmapStore.getState().setNodeDrawerOpen(true);
                        }, 150);
                      }}
                    >
                      <PrereqStatusIcon className={cn("w-4 h-4", statusColors[prereqStatus])} />
                      <div className="flex-1">
                        <div className="text-sm font-medium">{prereq.title}</div>
                        <div className="text-xs text-muted-foreground">{prereq.code}</div>
                      </div>
                      <ArrowRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* What comes next */}
          {dependents.length > 0 && (
            <div className="space-y-3">
              <div className="text-sm font-medium">Unlocks these courses</div>
              <div className="space-y-2">
                {dependents.map((dependent) => {
                  const dependentStatus = getNodeStatus(path.slug, dependent.id);
                  const DependentStatusIcon = statusIcons[dependentStatus];
                  
                  return (
                    <div 
                      key={dependent.id}
                      className="flex items-center gap-3 p-2 rounded-lg border border-border cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => {
                        setNodeDrawerOpen(false);
                        setTimeout(() => {
                          useRoadmapStore.getState().setSelectedNode(dependent.id);
                          useRoadmapStore.getState().setNodeDrawerOpen(true);
                        }, 150);
                      }}
                    >
                      <DependentStatusIcon className={cn("w-4 h-4", statusColors[dependentStatus])} />
                      <div className="flex-1">
                        <div className="text-sm font-medium">{dependent.title}</div>
                        <div className="text-xs text-muted-foreground">{dependent.code}</div>
                      </div>
                      <ArrowRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tags */}
          {selectedNode.tags.length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-medium">Tags</div>
              <div className="flex flex-wrap gap-2">
                {selectedNode.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <Separator />

          {/* WWU Resources */}
          <div className="space-y-3">
            <div className="text-sm font-medium">WWU CS Resources</div>
            <div className="space-y-2">
              {path.wwuLinks.map((link, index) => {
                const linkNames = [
                  'CS Department Homepage',
                  'Resources & Information',
                  'Scholarship Awards',
                  'Student Survival Guide'
                ];
                
                return (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    asChild
                    className="w-full justify-between"
                  >
                    <a href={link} target="_blank" rel="noopener noreferrer">
                      <span>{linkNames[index] || `Resource ${index + 1}`}</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </Button>
                );
              })}
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};