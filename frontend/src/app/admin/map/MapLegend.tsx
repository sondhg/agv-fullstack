/**
 * Component for displaying a legend explaining map visualization elements
 */
export const MapLegend = () => {
  return (
    <div className="mt-2 grid grid-cols-3 gap-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm">
      {/* AGV Motion State Indicators */}
      <div>
        <h4 className="mb-2 font-semibold">AGV Motion State</h4>{" "}
        <div className="space-y-2">
          <div className="flex items-center">
            <div className="mr-2 h-4 w-4 rounded-full bg-yellow-500"></div>
            <span>Idle</span>
          </div>
          <div className="flex items-center">
            <div className="mr-2 h-4 w-4 rounded-full bg-green-500"></div>
            <span>Moving</span>
          </div>
          <div className="flex items-center">
            <div className="mr-2 h-4 w-4 rounded-full bg-red-500"></div>
            <span>Waiting</span>
          </div>
        </div>
      </div>

      {/* Map Elements */}
      <div>
        <h4 className="mb-2 font-semibold">Map Elements</h4>
        <div className="space-y-2">
          <div className="flex items-center">
            <svg width="20" height="20" viewBox="0 0 20 20" className="mr-2">
              <circle
                cx="10"
                cy="10"
                r="6"
                fill="white"
                stroke="black"
                strokeWidth="2"
              />
            </svg>
            <span>Node</span>
          </div>
          <div className="flex items-center">
            <svg width="20" height="20" viewBox="0 0 20 20" className="mr-2">
              <line
                x1="2"
                y1="10"
                x2="18"
                y2="10"
                stroke="black"
                strokeWidth="2"
              />
            </svg>
            <span>Connection</span>
          </div>{" "}
          <div className="flex items-center">
            <svg width="20" height="20" viewBox="0 0 20 20" className="mr-2">
              <line
                x1="2"
                y1="10"
                x2="18"
                y2="10"
                stroke="red"
                strokeWidth="3"
              />
              <polygon points="14,7 18,10 14,13" fill="red" />
            </svg>
            <span>AGV Path</span>
          </div>
        </div>
      </div>

      {/* Path Direction */}
      <div>
        <h4 className="mb-2 font-semibold">Path Direction</h4>
        <div className="space-y-2">
          <div className="flex items-center">
            <svg width="20" height="20" viewBox="0 0 20 20" className="mr-2">
              <defs>
                {" "}
                <marker
                  id="arrowhead-legend"
                  markerWidth="6"
                  markerHeight="4"
                  refX="6"
                  refY="2"
                  orient="auto"
                >
                  <polygon points="0 0, 6 2, 0 4" fill="red" />
                </marker>
              </defs>
              <line
                x1="2"
                y1="10"
                x2="15"
                y2="10"
                stroke="red"
                strokeWidth="2"
                markerEnd="url(#arrowhead-legend)"
              />
            </svg>
            <span>Movement Direction</span>
          </div>{" "}
          <div className="mt-2 flex items-center">
            <p className="text-xs text-slate-600">
              * Animated arrows show movement direction along paths
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
