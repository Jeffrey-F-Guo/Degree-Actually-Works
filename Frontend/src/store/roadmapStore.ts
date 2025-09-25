import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { NodeStatus, UserProgress, RoadmapPath } from '@/types/roadmap';

interface RoadmapState {
  currentPath: RoadmapPath | null;
  userProgress: Record<string, UserProgress>; // keyed by pathSlug
  selectedNodeId: string | null;
  isNodeDrawerOpen: boolean;
  searchQuery: string;
  hiddenGroups: string[];
  isAuthenticated: boolean;
  userId: string | null;
  
  // Actions
  setCurrentPath: (path: RoadmapPath) => void;
  setNodeStatus: (pathSlug: string, nodeId: string, status: NodeStatus) => void;
  getNodeStatus: (pathSlug: string, nodeId: string) => NodeStatus;
  setSelectedNode: (nodeId: string | null) => void;
  setNodeDrawerOpen: (open: boolean) => void;
  setSearchQuery: (query: string) => void;
  toggleGroupVisibility: (groupTitle: string) => void;
  getPathProgress: (pathSlug: string) => { completed: number; total: number; percentage: number };
  getGroupProgress: (pathSlug: string, nodes: string[]) => { completed: number; total: number; percentage: number };
  exportProgress: (pathSlug: string) => string;
  importProgress: (pathSlug: string, data: string) => boolean;
  generateShareableUrl: (pathSlug: string) => string;
  loadFromShareableUrl: (url: string) => boolean;
  
  // Backend integration actions (placeholders)
  setAuthState: (isAuthenticated: boolean, userId?: string) => void;
  syncProgressToBackend: (pathSlug: string) => Promise<boolean>;
  loadProgressFromBackend: (pathSlug: string) => Promise<boolean>;
  loadPathsFromBackend: () => Promise<RoadmapPath[]>;
}

export const useRoadmapStore = create<RoadmapState>()(
  persist(
    (set, get) => ({
      currentPath: null,
      userProgress: {},
      selectedNodeId: null,
      isNodeDrawerOpen: false,
      searchQuery: '',
      hiddenGroups: [],
      isAuthenticated: false,
      userId: null,

      setCurrentPath: (path) => set({ currentPath: path }),

      setNodeStatus: (pathSlug, nodeId, status) =>
        set((state) => ({
          userProgress: {
            ...state.userProgress,
            [pathSlug]: {
              ...state.userProgress[pathSlug],
              [nodeId]: {
                status,
                updatedAt: new Date().toISOString(),
              },
            },
          },
        })),

      getNodeStatus: (pathSlug, nodeId) => {
        const progress = get().userProgress[pathSlug];
        return progress?.[nodeId]?.status || 'not-started';
      },

      setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),

      setNodeDrawerOpen: (open) => set({ isNodeDrawerOpen: open }),

      setSearchQuery: (query) => set({ searchQuery: query }),

      toggleGroupVisibility: (groupTitle) =>
        set((state) => ({
          hiddenGroups: state.hiddenGroups.includes(groupTitle)
            ? state.hiddenGroups.filter((g) => g !== groupTitle)
            : [...state.hiddenGroups, groupTitle],
        })),

      getPathProgress: (pathSlug) => {
        const progress = get().userProgress[pathSlug] || {};
        const path = get().currentPath;
        
        if (!path) return { completed: 0, total: 0, percentage: 0 };
        
        const allNodes = path.groups.flatMap((group) => group.nodes);
        const completed = allNodes.filter(
          (node) => progress[node.id]?.status === 'completed'
        ).length;
        
        return {
          completed,
          total: allNodes.length,
          percentage: allNodes.length > 0 ? Math.round((completed / allNodes.length) * 100) : 0,
        };
      },

      getGroupProgress: (pathSlug, nodeIds) => {
        const progress = get().userProgress[pathSlug] || {};
        const completed = nodeIds.filter(
          (nodeId) => progress[nodeId]?.status === 'completed'
        ).length;
        
        return {
          completed,
          total: nodeIds.length,
          percentage: nodeIds.length > 0 ? Math.round((completed / nodeIds.length) * 100) : 0,
        };
      },

      exportProgress: (pathSlug) => {
        const progress = get().userProgress[pathSlug] || {};
        return JSON.stringify(progress, null, 2);
      },

      importProgress: (pathSlug, data) => {
        try {
          const progress = JSON.parse(data);
          set((state) => ({
            userProgress: {
              ...state.userProgress,
              [pathSlug]: progress,
            },
          }));
          return true;
        } catch {
          return false;
        }
      },

      generateShareableUrl: (pathSlug) => {
        const progress = get().userProgress[pathSlug] || {};
        const simpleProgress = Object.entries(progress).reduce(
          (acc, [nodeId, data]) => {
            if (data.status !== 'not-started') {
              acc[nodeId] = data.status;
            }
            return acc;
          },
          {} as Record<string, NodeStatus>
        );
        
        const shareData = { pathSlug, progress: simpleProgress };
        const encoded = btoa(JSON.stringify(shareData));
        return `${window.location.origin}/path/${pathSlug}?share=${encoded}`;
      },

      loadFromShareableUrl: (url) => {
        try {
          const urlObj = new URL(url);
          const shareParam = urlObj.searchParams.get('share');
          if (!shareParam) return false;
          
          const decoded = JSON.parse(atob(shareParam));
          const { pathSlug, progress } = decoded;
          
          const fullProgress = Object.entries(progress).reduce(
            (acc, [nodeId, status]) => {
              acc[nodeId] = {
                status: status as NodeStatus,
                updatedAt: new Date().toISOString(),
              };
              return acc;
            },
            {} as UserProgress
          );
          
          set((state) => ({
            userProgress: {
              ...state.userProgress,
              [pathSlug]: fullProgress,
            },
          }));
          
          return true;
        } catch {
          return false;
        }
      },

      // Backend integration actions (placeholders)
      setAuthState: (isAuthenticated, userId) => 
        set({ isAuthenticated, userId: userId || null }),

      syncProgressToBackend: async (pathSlug) => {
        // TODO: Implement API call to save progress
        const progress = get().userProgress[pathSlug];
        const userId = get().userId;
        
        if (!userId || !progress) return false;
        
        try {
          // Placeholder for API call
          console.log('Syncing progress to backend:', { pathSlug, userId, progress });
          return true;
        } catch (error) {
          console.error('Failed to sync progress:', error);
          return false;
        }
      },

      loadProgressFromBackend: async (pathSlug) => {
        // TODO: Implement API call to load progress
        const userId = get().userId;
        
        if (!userId) return false;
        
        try {
          // Placeholder for API call
          console.log('Loading progress from backend:', { pathSlug, userId });
          return true;
        } catch (error) {
          console.error('Failed to load progress:', error);
          return false;
        }
      },

      loadPathsFromBackend: async () => {
        // TODO: Implement API call to load paths
        try {
          // Placeholder for API call
          console.log('Loading paths from backend');
          return [];
        } catch (error) {
          console.error('Failed to load paths:', error);
          return [];
        }
      },
    }),
    {
      name: 'roadmap-storage',
      partialize: (state) => ({
        userProgress: state.userProgress,
        hiddenGroups: state.hiddenGroups,
        isAuthenticated: state.isAuthenticated,
        userId: state.userId,
      }),
    }
  )
);