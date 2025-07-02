"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MiniNavbar } from "@/components/Header";
import { cn } from "@/lib/utils";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";

// Canvas effect components (copied from homepage)
type Uniforms = {
  [key: string]: {
    value: number[] | number[][] | number;
    type: string;
  };
};

interface ShaderProps {
  source: string;
  uniforms: {
    [key: string]: {
      value: number[] | number[][] | number;
      type: string;
    };
  };
  maxFps?: number;
}

export const CanvasRevealEffect = ({
  animationSpeed = 10,
  opacities = [0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8, 1],
  colors = [[0, 255, 255]],
  containerClassName,
  dotSize,
  showGradient = true,
  reverse = false,
}: {
  animationSpeed?: number;
  opacities?: number[];
  colors?: number[][];
  containerClassName?: string;
  dotSize?: number;
  showGradient?: boolean;
  reverse?: boolean;
}) => {
  return (
    <div className={cn("h-full relative w-full", containerClassName)}>
      <div className="h-full w-full">
        <DotMatrix
          colors={colors ?? [[0, 255, 255]]}
          dotSize={dotSize ?? 3}
          opacities={
            opacities ?? [0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8, 1]
          }
          shader={`
            ${reverse ? 'u_reverse_active' : 'false'}_;
            animation_speed_factor_${animationSpeed.toFixed(1)}_;
          `}
          center={["x", "y"]}
        />
      </div>
      {showGradient && (
        <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent" />
      )}
    </div>
  );
};

interface DotMatrixProps {
  colors?: number[][];
  opacities?: number[];
  totalSize?: number;
  dotSize?: number;
  shader?: string;
  center?: ("x" | "y")[];
}

const DotMatrix: React.FC<DotMatrixProps> = ({
  colors = [[0, 0, 0]],
  opacities = [0.04, 0.04, 0.04, 0.04, 0.04, 0.08, 0.08, 0.08, 0.08, 0.14],
  totalSize = 20,
  dotSize = 2,
  shader = "",
  center = ["x", "y"],
}) => {
  const uniforms = React.useMemo(() => {
    let colorsArray = [
      colors[0],
      colors[0],
      colors[0],
      colors[0],
      colors[0],
      colors[0],
    ];
    if (colors.length === 2) {
      colorsArray = [
        colors[0],
        colors[0],
        colors[0],
        colors[1],
        colors[1],
        colors[1],
      ];
    } else if (colors.length === 3) {
      colorsArray = [
        colors[0],
        colors[0],
        colors[1],
        colors[1],
        colors[2],
        colors[2],
      ];
    }
    return {
      u_colors: {
        value: colorsArray.map((color) => [
          color[0] / 255,
          color[1] / 255,
          color[2] / 255,
        ]),
        type: "uniform3fv",
      },
      u_opacities: {
        value: opacities,
        type: "uniform1fv",
      },
      u_total_size: {
        value: totalSize,
        type: "uniform1f",
      },
      u_dot_size: {
        value: dotSize,
        type: "uniform1f",
      },
      u_reverse: {
        value: shader.includes("u_reverse_active") ? 1 : 0,
        type: "uniform1i",
      },
    };
  }, [colors, opacities, totalSize, dotSize, shader]);

  return (
    <Shader
      source={`
        precision mediump float;
        in vec2 fragCoord;

        uniform float u_time;
        uniform float u_opacities[10];
        uniform vec3 u_colors[6];
        uniform float u_total_size;
        uniform float u_dot_size;
        uniform vec2 u_resolution;
        uniform int u_reverse;

        out vec4 fragColor;

        float PHI = 1.61803398874989484820459;
        float random(vec2 xy) {
            return fract(tan(distance(xy * PHI, xy) * 0.5) * xy.x);
        }

        void main() {
            vec2 st = fragCoord.xy;
            ${
              center.includes("x")
                ? "st.x -= abs(floor((mod(u_resolution.x, u_total_size) - u_dot_size) * 0.5));"
                : ""
            }
            ${
              center.includes("y")
                ? "st.y -= abs(floor((mod(u_resolution.y, u_total_size) - u_dot_size) * 0.5));"
                : ""
            }

            float opacity = step(0.0, st.x);
            opacity *= step(0.0, st.y);

            vec2 st2 = vec2(int(st.x / u_total_size), int(st.y / u_total_size));

            float frequency = 5.0;
            float show_offset = random(st2);
            float rand = random(st2 * floor((u_time / frequency) + show_offset + frequency));
            opacity *= u_opacities[int(rand * 10.0)];
            opacity *= 1.0 - step(u_dot_size / u_total_size, fract(st.x / u_total_size));
            opacity *= 1.0 - step(u_dot_size / u_total_size, fract(st.y / u_total_size));

            vec3 color = u_colors[int(show_offset * 6.0)];

            float animation_speed_factor = 0.5;
            vec2 center_grid = u_resolution / 2.0 / u_total_size;
            float dist_from_center = distance(center_grid, st2);

            float timing_offset_intro = dist_from_center * 0.01 + (random(st2) * 0.15);
            float max_grid_dist = distance(center_grid, vec2(0.0, 0.0));
            float timing_offset_outro = (max_grid_dist - dist_from_center) * 0.02 + (random(st2 + 42.0) * 0.2);

            float current_timing_offset;
            if (u_reverse == 1) {
                current_timing_offset = timing_offset_outro;
                opacity *= 1.0 - step(current_timing_offset, u_time * animation_speed_factor);
                opacity *= clamp((step(current_timing_offset + 0.1, u_time * animation_speed_factor)) * 1.25, 1.0, 1.25);
            } else {
                current_timing_offset = timing_offset_intro;
                opacity *= step(current_timing_offset, u_time * animation_speed_factor);
                opacity *= clamp((1.0 - step(current_timing_offset + 0.1, u_time * animation_speed_factor)) * 1.25, 1.0, 1.25);
            }

            fragColor = vec4(color, opacity);
            fragColor.rgb *= fragColor.a;
        }`}
      uniforms={uniforms}
      maxFps={60}
    />
  );
};

const ShaderMaterial = ({
  source,
  uniforms,
  maxFps = 60,
}: {
  source: string;
  maxFps?: number;
  uniforms: Uniforms;
}) => {
  const { size } = useThree();
  const ref = React.useRef<THREE.Mesh>(null);
  let lastFrameTime = 0;

  useFrame(({ clock }) => {
    if (!ref.current) return;
    const timestamp = clock.getElapsedTime();
    lastFrameTime = timestamp;
    const material: any = ref.current.material;
    const timeLocation = material.uniforms.u_time;
    timeLocation.value = timestamp;
  });

  const getUniforms = () => {
    const preparedUniforms: any = {};
    for (const uniformName in uniforms) {
      const uniform: any = uniforms[uniformName];
      switch (uniform.type) {
        case "uniform1f":
          preparedUniforms[uniformName] = { value: uniform.value, type: "1f" };
          break;
        case "uniform1i":
          preparedUniforms[uniformName] = { value: uniform.value, type: "1i" };
          break;
        case "uniform3f":
          preparedUniforms[uniformName] = {
            value: new THREE.Vector3().fromArray(uniform.value),
            type: "3f",
          };
          break;
        case "uniform1fv":
          preparedUniforms[uniformName] = { value: uniform.value, type: "1fv" };
          break;
        case "uniform3fv":
          preparedUniforms[uniformName] = {
            value: uniform.value.map((v: number[]) =>
              new THREE.Vector3().fromArray(v)
            ),
            type: "3fv",
          };
          break;
        case "uniform2f":
          preparedUniforms[uniformName] = {
            value: new THREE.Vector2().fromArray(uniform.value),
            type: "2f",
          };
          break;
        default:
          console.error(`Invalid uniform type for '${uniformName}'.`);
          break;
      }
    }
    preparedUniforms["u_time"] = { value: 0, type: "1f" };
    preparedUniforms["u_resolution"] = {
      value: new THREE.Vector2(size.width * 2, size.height * 2),
    };
    return preparedUniforms;
  };

  const material = React.useMemo(() => {
    const materialObject = new THREE.ShaderMaterial({
      vertexShader: `
      precision mediump float;
      in vec2 coordinates;
      uniform vec2 u_resolution;
      out vec2 fragCoord;
      void main(){
        float x = position.x;
        float y = position.y;
        gl_Position = vec4(x, y, 0.0, 1.0);
        fragCoord = (position.xy + vec2(1.0)) * 0.5 * u_resolution;
        fragCoord.y = u_resolution.y - fragCoord.y;
      }
      `,
      fragmentShader: source,
      uniforms: getUniforms(),
      glslVersion: THREE.GLSL3,
      blending: THREE.CustomBlending,
      blendSrc: THREE.SrcAlphaFactor,
      blendDst: THREE.OneFactor,
    });
    return materialObject;
  }, [size.width, size.height, source]);

  return (
    <mesh ref={ref as any}>
      <planeGeometry args={[2, 2]} />
      <primitive object={material} attach="material" />
    </mesh>
  );
};

const Shader: React.FC<ShaderProps> = ({ source, uniforms, maxFps = 60 }) => {
  return (
    <Canvas className="absolute inset-0 h-full w-full">
      <ShaderMaterial source={source} uniforms={uniforms} maxFps={maxFps} />
    </Canvas>
  );
};

interface BrandData {
  name: string;
  website: string;
  country: string;
  description?: string;
  industry?: string;
  competitors?: Array<{
    name: string;
    website: string;
    reason: string;
  }>;
}

interface AnalysisResult {
  queries?: Array<{
    topic: string;
    prompt: string;
  }>;
  analysis?: any;
}

export default function AnalysisPage() {
  const [step, setStep] = useState<"brand-details" | "analyzing" | "competitors" | "generating" | "results">("brand-details");
  const [brandData, setBrandData] = useState<BrandData>({
    name: "",
    website: "",
    country: "United States"
  });
  const [analysisStatus, setAnalysisStatus] = useState("");
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [selectedCompetitors, setSelectedCompetitors] = useState<string[]>([]);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleBrandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!brandData.name || !brandData.website) return;

    setStep("analyzing");
    setIsLoading(true);
    setAnalysisStatus("Starting brand analysis...");
    setAnalysisProgress(0);

    try {
      const response = await fetch("http://localhost:5000/stream-brand-info", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          brandName: brandData.name,
          brandWebsite: brandData.website,
          brandCountry: brandData.country,
        }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.error) {
                console.error("Analysis error:", data.error);
                setAnalysisStatus("Error: " + data.error);
                return;
              }

              if (data.status) {
                setAnalysisStatus(data.status);
                
                // Update progress based on step
                switch (data.step) {
                  case "init":
                    setAnalysisProgress(10);
                    break;
                  case "description":
                    setAnalysisProgress(25);
                    break;
                  case "industry":
                    setAnalysisProgress(50);
                    break;
                  case "competitors":
                    setAnalysisProgress(75);
                    break;
                  case "name":
                    setAnalysisProgress(90);
                    break;
                  case "complete":
                    setAnalysisProgress(100);
                    if (data.result) {
                      setBrandData(prev => ({
                        ...prev,
                        description: data.result.description,
                        industry: data.result.industry,
                        competitors: data.result.competitors?.competitors || []
                      }));
                      setStep("competitors");
                    }
                    break;
                }
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Analysis failed:", error);
      setAnalysisStatus("Analysis failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompetitorSelection = (competitorName: string) => {
    setSelectedCompetitors(prev => 
      prev.includes(competitorName)
        ? prev.filter(name => name !== competitorName)
        : [...prev, competitorName]
    );
  };

  const handleGenerateReport = async () => {
    setStep("generating");
    setIsLoading(true);
    setAnalysisStatus("Generating queries...");
    setAnalysisProgress(0);

    try {
      // First generate queries
      const queryResponse = await fetch("http://localhost:5000/stream-generate-queries", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          brandName: brandData.name,
          brandDescription: brandData.description,
          brandIndustry: brandData.industry,
          brandCountry: brandData.country,
          totalQueries: 10,
        }),
      });

      if (!queryResponse.body) throw new Error("No response body for queries");

      const queryReader = queryResponse.body.getReader();
      const queryDecoder = new TextDecoder();
      let queries: any[] = [];

      while (true) {
        const { done, value } = await queryReader.read();
        if (done) break;

        const chunk = queryDecoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.error) {
                console.error("Query generation error:", data.error);
                setAnalysisStatus("Error: " + data.error);
                return;
              }

              if (data.status) {
                setAnalysisStatus(data.status);
                
                switch (data.step) {
                  case "init":
                    setAnalysisProgress(10);
                    break;
                  case "generating":
                    setAnalysisProgress(50);
                    break;
                  case "complete":
                    setAnalysisProgress(75);
                    if (data.result?.queries) {
                      queries = data.result.queries;
                    }
                    break;
                }
              }
            } catch (e) {
              console.error("Error parsing query SSE data:", e);
            }
          }
        }
      }

      // Then test the queries
      setAnalysisStatus("Running GEO analysis...");
      
      const testResponse = await fetch("http://localhost:5000/stream-test-queries", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          brandName: brandData.name,
          queries: queries,
          competitors: selectedCompetitors,
          models: ["gpt-4o-mini-2024-07-18"],
        }),
      });

      if (!testResponse.body) throw new Error("No response body for analysis");

      const testReader = testResponse.body.getReader();
      const testDecoder = new TextDecoder();

      while (true) {
        const { done, value } = await testReader.read();
        if (done) break;

        const chunk = testDecoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.error) {
                console.error("Analysis error:", data.error);
                setAnalysisStatus("Error: " + data.error);
                return;
              }

              if (data.status) {
                setAnalysisStatus(data.status);
                
                if (data.progress) {
                  setAnalysisProgress(75 + (data.progress * 0.25));
                }

                if (data.step === "complete" && data.result) {
                  setAnalysisResult({
                    queries: queries,
                    analysis: data.result
                  });
                  setStep("results");
                  setAnalysisProgress(100);
                }
              }
            } catch (e) {
              console.error("Error parsing analysis SSE data:", e);
            }
          }
        }
      }

    } catch (error) {
      console.error("Report generation failed:", error);
      setAnalysisStatus("Report generation failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn("flex w-[100%] flex-col min-h-screen bg-black relative text-white")}>
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0">
          <CanvasRevealEffect
            animationSpeed={3}
            containerClassName="bg-black"
            colors={[
              [255, 255, 255],
              [255, 255, 255],
            ]}
            dotSize={6}
            reverse={false}
          />
        </div>
        
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(0,0,0,1)_0%,_transparent_100%)]" />
        <div className="absolute top-0 left-0 right-0 h-1/3 bg-gradient-to-b from-black to-transparent" />
      </div>
      
      {/* Content Layer */}
      <div className="relative z-10 flex flex-col flex-1">
        {/* Top navigation */}
        <MiniNavbar />

        {/* Main content container */}
        <div className="flex flex-1 flex-col lg:flex-row overflow-hidden">
          {/* Center content (same spacing as homepage) */}
          <div className="flex-1 flex flex-col justify-center items-center py-4">
            <div className="w-full max-w-4xl px-4 h-full flex flex-col justify-center">
        <AnimatePresence mode="wait">
          {step === "brand-details" && (
            <motion.div
              key="brand-details"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <div className="text-center space-y-3">
                <h1 className="text-3xl font-bold text-white">
                  Tell us about your brand
                </h1>
                <p className="text-lg text-gray-400">
                  We'll analyze how your brand appears in AI search results
                </p>
              </div>

              <form onSubmit={handleBrandSubmit} className="space-y-4 max-w-md mx-auto">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Brand Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={brandData.name}
                    onChange={(e) => setBrandData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0CF2A0] focus:border-transparent"
                    placeholder="e.g., Apple, Tesla, etc."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Website *
                  </label>
                  <input
                    type="url"
                    required
                    value={brandData.website}
                    onChange={(e) => setBrandData(prev => ({ ...prev, website: e.target.value }))}
                    className="w-full px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0CF2A0] focus:border-transparent"
                    placeholder="https://your-website.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Primary Market
                  </label>
                  <select
                    value={brandData.country}
                    onChange={(e) => setBrandData(prev => ({ ...prev, country: e.target.value }))}
                    className="w-full px-4 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-[#0CF2A0] focus:border-transparent"
                  >
                    <option value="United States">United States</option>
                    <option value="United Kingdom">United Kingdom</option>
                    <option value="Canada">Canada</option>
                    <option value="Australia">Australia</option>
                    <option value="Germany">Germany</option>
                    <option value="France">France</option>
                    <option value="world">Global</option>
                  </select>
                </div>

                <motion.button
                  type="submit"
                  disabled={!brandData.name || !brandData.website}
                  className="w-full bg-[#0CF2A0] text-black font-semibold py-2 px-6 rounded-lg hover:bg-opacity-90 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Analyze My Brand
                </motion.button>
              </form>
            </motion.div>
          )}

          {step === "analyzing" && (
            <motion.div
              key="analyzing"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8 text-center"
            >
              <div className="space-y-4">
                <h1 className="text-4xl font-bold text-white">
                  Analyzing {brandData.name}
                </h1>
                <p className="text-xl text-gray-400">
                  {analysisStatus}
                </p>
              </div>

              <div className="max-w-lg mx-auto">
                <div className="bg-gray-900/50 rounded-full h-4 overflow-hidden border border-gray-700/50">
                  <motion.div
                    className="h-full bg-gradient-to-r from-[#0CF2A0] to-[#0CF2A0]/80 relative"
                    initial={{ width: 0 }}
                    animate={{ width: `${analysisProgress}%` }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
                  </motion.div>
                </div>
                <div className="flex justify-between items-center mt-3">
                  <p className="text-sm text-gray-400">{analysisProgress}% complete</p>
                  <p className="text-sm text-[#0CF2A0] font-medium">Step {Math.ceil(analysisProgress / 25)} of 4</p>
                </div>
              </div>
            </motion.div>
          )}

          {step === "competitors" && (
            <motion.div
              key="competitors"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="h-full flex flex-col"
            >
              <div className="text-center space-y-2 mb-6">
                <h1 className="text-3xl font-bold text-white">
                  Select Your Competitors
                </h1>
                <p className="text-lg text-gray-400">
                  Choose which companies you want to compare against ({brandData.competitors?.length || 0} found)
                </p>
              </div>

              <div className="flex-1 overflow-y-auto pr-2">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-w-5xl mx-auto">
                {brandData.competitors?.map((competitor, index) => (
                  <motion.div
                    key={competitor.name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={cn(
                      "p-3 rounded-lg border cursor-pointer transition-all duration-200 aspect-square flex flex-col min-h-[140px]",
                      selectedCompetitors.includes(competitor.name)
                        ? "border-[#0CF2A0] bg-[#0CF2A0]/10"
                        : "border-gray-700 bg-gray-900 hover:border-gray-600"
                    )}
                    onClick={() => handleCompetitorSelection(competitor.name)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-white text-base leading-tight">{competitor.name}</h3>
                      <div className={cn(
                        "w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0",
                        selectedCompetitors.includes(competitor.name)
                          ? "border-[#0CF2A0] bg-[#0CF2A0]"
                          : "border-gray-600"
                      )}>
                        {selectedCompetitors.includes(competitor.name) && (
                          <svg className="w-3 h-3 text-black" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    </div>
                    <div className="flex-1 flex flex-col justify-between">
                      <div>
                        <p className="text-xs text-gray-400 mb-1 truncate">{competitor.website}</p>
                        <p className="text-xs text-gray-500 overflow-hidden" style={{
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical'
                        }}>{competitor.reason}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
                </div>
              </div>

              <div className="text-center pt-4 pb-2">
                <motion.button
                  onClick={handleGenerateReport}
                  disabled={selectedCompetitors.length === 0}
                  className="bg-[#0CF2A0] text-black font-semibold py-2 px-6 rounded-lg hover:bg-opacity-90 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Generate Report ({selectedCompetitors.length} selected)
                </motion.button>
              </div>
            </motion.div>
          )}

          {step === "generating" && (
            <motion.div
              key="generating"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8 text-center"
            >
              <div className="space-y-4">
                <h1 className="text-4xl font-bold text-white">
                  Generating Your Report
                </h1>
                <p className="text-xl text-gray-400">
                  {analysisStatus}
                </p>
              </div>

              <div className="max-w-lg mx-auto">
                <div className="bg-gray-900/50 rounded-full h-4 overflow-hidden border border-gray-700/50">
                  <motion.div
                    className="h-full bg-gradient-to-r from-[#0CF2A0] to-[#0CF2A0]/80 relative"
                    initial={{ width: 0 }}
                    animate={{ width: `${analysisProgress}%` }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
                  </motion.div>
                </div>
                <div className="flex justify-between items-center mt-3">
                  <p className="text-sm text-gray-400">{Math.round(analysisProgress)}% complete</p>
                  <p className="text-sm text-[#0CF2A0] font-medium">Generating Report...</p>
                </div>
              </div>
            </motion.div>
          )}

          {step === "results" && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8"
            >
              <div className="text-center space-y-4">
                <h1 className="text-4xl font-bold text-white">
                  Your AI Search Report
                </h1>
                <p className="text-xl text-gray-400">
                  Analysis complete for {brandData.name}
                </p>
              </div>

              <div className="bg-gray-900 rounded-lg p-6">
                <h2 className="text-2xl font-semibold text-white mb-4">Executive Summary</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-[#0CF2A0]">
                      {analysisResult.queries?.length || 0}
                    </div>
                    <div className="text-sm text-gray-400">Queries Tested</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-[#0CF2A0]">
                      {selectedCompetitors.length}
                    </div>
                    <div className="text-sm text-gray-400">Competitors Analyzed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-[#0CF2A0]">
                      {analysisResult.analysis?.optimization_suggestions?.length || 0}
                    </div>
                    <div className="text-sm text-gray-400">Recommendations</div>
                  </div>
                </div>

                {analysisResult.analysis?.optimization_suggestions && (
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold text-white">Key Recommendations</h3>
                    <div className="space-y-3">
                      {analysisResult.analysis.optimization_suggestions.slice(0, 5).map((suggestion: string, index: number) => (
                        <div key={index} className="flex items-start space-x-3">
                          <div className="w-6 h-6 rounded-full bg-[#0CF2A0] flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-black text-sm font-bold">{index + 1}</span>
                          </div>
                          <p className="text-gray-300">{suggestion}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-8 text-center">
                  <motion.button
                    onClick={() => {
                      const dataStr = JSON.stringify(analysisResult, null, 2);
                      const dataBlob = new Blob([dataStr], { type: 'application/json' });
                      const url = URL.createObjectURL(dataBlob);
                      const link = document.createElement('a');
                      link.href = url;
                      link.download = `${brandData.name.toLowerCase().replace(/\s+/g, '-')}-ai-search-report.json`;
                      link.click();
                    }}
                    className="bg-[#0CF2A0] text-black font-semibold py-3 px-8 rounded-lg hover:bg-opacity-90 transition-colors duration-200"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Download Full Report
                  </motion.button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}