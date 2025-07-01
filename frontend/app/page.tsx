"use client";

import React, { useState,useMemo, useRef, useEffect, type FormEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import RotatingText from "@/components/RotatingText";
import { MiniNavbar } from "@/components/Header";

import * as THREE from "three";

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

interface SignInPageProps {
  className?: string;
}
      
export const CanvasRevealEffect = ({
  animationSpeed = 10,
  opacities = [0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8, 1],
  colors = [[0, 255, 255]],
  containerClassName,
  dotSize,
  showGradient = true,
  reverse = false, // This controls the direction
}: {
  animationSpeed?: number;
  opacities?: number[];
  colors?: number[][];
  containerClassName?: string;
  dotSize?: number;
  showGradient?: boolean;
  reverse?: boolean; // This prop determines the direction
}) => {
  return (
    <div className={cn("h-full relative w-full", containerClassName)}> {/* Removed bg-white */}
      <div className="h-full w-full">
        <DotMatrix
          colors={colors ?? [[0, 255, 255]]}
          dotSize={dotSize ?? 3}
          opacities={
            opacities ?? [0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8, 1]
          }
          // Pass reverse state and speed via string flags in the empty shader prop
          shader={`
            ${reverse ? 'u_reverse_active' : 'false'}_;
            animation_speed_factor_${animationSpeed.toFixed(1)}_;
          `}
          center={["x", "y"]}
        />
      </div>
      {showGradient && (
        // Adjust gradient colors if needed based on background (was bg-white, now likely uses containerClassName bg)
        // Example assuming a dark background like the SignInPage uses:
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
  shader = "", // This shader string will now contain the animation logic
  center = ["x", "y"],
}) => {
  // ... uniforms calculation remains the same for colors, opacities, etc.
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
        value: shader.includes("u_reverse_active") ? 1 : 0, // Convert boolean to number (1 or 0)
        type: "uniform1i", // Use 1i for bool in WebGL1/GLSL100, or just bool for GLSL300+ if supported
      },
    };
  }, [colors, opacities, totalSize, dotSize, shader]); // Add shader to dependencies

  return (
    <Shader
      // The main animation logic is now built *outside* the shader prop
      source={`
        precision mediump float;
        in vec2 fragCoord;

        uniform float u_time;
        uniform float u_opacities[10];
        uniform vec3 u_colors[6];
        uniform float u_total_size;
        uniform float u_dot_size;
        uniform vec2 u_resolution;
        uniform int u_reverse; // Changed from bool to int

        out vec4 fragColor;

        float PHI = 1.61803398874989484820459;
        float random(vec2 xy) {
            return fract(tan(distance(xy * PHI, xy) * 0.5) * xy.x);
        }
        float map(float value, float min1, float max1, float min2, float max2) {
            return min2 + (value - min1) * (max2 - min2) / (max1 - min1);
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
            float show_offset = random(st2); // Used for initial opacity random pick and color
            float rand = random(st2 * floor((u_time / frequency) + show_offset + frequency));
            opacity *= u_opacities[int(rand * 10.0)];
            opacity *= 1.0 - step(u_dot_size / u_total_size, fract(st.x / u_total_size));
            opacity *= 1.0 - step(u_dot_size / u_total_size, fract(st.y / u_total_size));

            vec3 color = u_colors[int(show_offset * 6.0)];

            // --- Animation Timing Logic ---
            float animation_speed_factor = 0.5; // Extract speed from shader string
            vec2 center_grid = u_resolution / 2.0 / u_total_size;
            float dist_from_center = distance(center_grid, st2);

            // Calculate timing offset for Intro (from center)
            float timing_offset_intro = dist_from_center * 0.01 + (random(st2) * 0.15);

            // Calculate timing offset for Outro (from edges)
            // Max distance from center to a corner of the grid
            float max_grid_dist = distance(center_grid, vec2(0.0, 0.0));
            float timing_offset_outro = (max_grid_dist - dist_from_center) * 0.02 + (random(st2 + 42.0) * 0.2);


            float current_timing_offset;
            if (u_reverse == 1) {
                current_timing_offset = timing_offset_outro;
                 // Outro logic: opacity starts high, goes to 0 when time passes offset
                 opacity *= 1.0 - step(current_timing_offset, u_time * animation_speed_factor);
                 // Clamp for fade-out transition
                 opacity *= clamp((step(current_timing_offset + 0.1, u_time * animation_speed_factor)) * 1.25, 1.0, 1.25);
            } else {
                current_timing_offset = timing_offset_intro;
                 // Intro logic: opacity starts 0, goes to base opacity when time passes offset
                 opacity *= step(current_timing_offset, u_time * animation_speed_factor);
                 // Clamp for fade-in transition
                 opacity *= clamp((1.0 - step(current_timing_offset + 0.1, u_time * animation_speed_factor)) * 1.25, 1.0, 1.25);
            }


            fragColor = vec4(color, opacity);
            fragColor.rgb *= fragColor.a; // Premultiply alpha
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
  hovered?: boolean;
  maxFps?: number;
  uniforms: Uniforms;
}) => {
  const { size } = useThree();
  const ref = useRef<THREE.Mesh>(null);
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
    }; // Initialize u_resolution
    return preparedUniforms;
  };

  // Shader material
  const material = useMemo(() => {
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
    <Canvas className="absolute inset-0  h-full w-full">
      <ShaderMaterial source={source} uniforms={uniforms} maxFps={maxFps} />
    </Canvas>
  );
};


export const SignInPage = ({ className }: SignInPageProps) => {
  const [email, setEmail] = useState("");
  const [step, setStep] = useState<"email" | "code" | "success">("email");
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const codeInputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);
  const [initialCanvasVisible, setInitialCanvasVisible] = useState(true);
  const [reverseCanvasVisible, setReverseCanvasVisible] = useState(false);

  const formVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      setStep("code");
    }
  };

  // Focus first input when code screen appears
  useEffect(() => {
    if (step === "code") {
      setTimeout(() => {
        codeInputRefs.current[0]?.focus();
      }, 500);
    }
  }, [step]);

  const handleCodeChange = (index: number, value: string) => {
    if (value.length <= 1) {
      const newCode = [...code];
      newCode[index] = value;
      setCode(newCode);
      
      // Focus next input if value is entered
      if (value && index < 5) {
        codeInputRefs.current[index + 1]?.focus();
      }
      
      // Check if code is complete
      if (index === 5 && value) {
        const isComplete = newCode.every(digit => digit.length === 1);
        if (isComplete) {
          // First show the new reverse canvas
          setReverseCanvasVisible(true);
          
          // Then hide the original canvas after a small delay
          setTimeout(() => {
            setInitialCanvasVisible(false);
          }, 50);
          
          // Transition to success screen after animation
          setTimeout(() => {
            setStep("success");
          }, 2000);
        }
      }
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !code[index] && index > 0) {
      codeInputRefs.current[index - 1]?.focus();
    }
  };

  const handleBackClick = () => {
    setStep("email");
    setCode(["", "", "", "", "", ""]);
    // Reset animations if going back
    setReverseCanvasVisible(false);
    setInitialCanvasVisible(true);
  };

  return (
    <div className={cn("flex w-[100%] flex-col min-h-screen bg-black relative", className)}>
      <div className="absolute inset-0 z-0">
        {/* Initial canvas (forward animation) */}
        {initialCanvasVisible && (
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
        )}
        
        {/* Reverse canvas (appears when code is complete) */}
        {reverseCanvasVisible && (
          <div className="absolute inset-0">
            <CanvasRevealEffect
              animationSpeed={4}
              containerClassName="bg-black"
              colors={[
                [255, 255, 255],
                [255, 255, 255],
              ]}
              dotSize={6}
              reverse={true}
            />
          </div>
        )}
        
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(0,0,0,1)_0%,_transparent_100%)]" />
        <div className="absolute top-0 left-0 right-0 h-1/3 bg-gradient-to-b from-black to-transparent" />
      </div>
      
      {/* Content Layer */}
      <div className="relative z-10 flex flex-col flex-1">
        {/* Top navigation */}
        <MiniNavbar />

        {/* Main content container */}
        <div className="flex flex-1 flex-col lg:flex-row ">
          {/* Left side (form) */}
          <div className="flex-1 flex flex-col justify-center items-center">
            <div className="w-full mt-[50px] max-w-sm">
              <AnimatePresence mode="wait">
                {step === "email" ? (
                  <motion.div 
                    key="email-step"
                    initial={{ opacity: 0, x: -100 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -100 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className="space-y-6 text-center"
                  >
                    <div className="space-y-1">
                      <motion.h1
                        variants={{
                          hidden: { opacity: 0, y: 20 },
                          visible: { opacity: 1, y: 0 }
                        }}
                        initial="hidden"
                        animate="visible"
                        className="text-4xl sm:text-5xl lg:text-[64px] font-semibold text-white leading-tight max-w-4xl mb-4"
                      >
                        Deliver collaborative<br />{' '}
                        <span className="inline-block h-[1.2em] sm:h-[1.2em] lg:h-[1.2em] overflow-hidden align-bottom">
                          <RotatingText
                            texts={['Support', 'Experiences', 'Relationships', 'Help', 'Service']}
                            mainClassName="text-[#0CF2A0] mx-1"
                            staggerFrom="last"
                            initial={{ y: "-100%", opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            exit={{ y: "110%", opacity: 0 }}
                            staggerDuration={0.01}
                            transition={{ type: "spring", damping: 18, stiffness: 250 }}
                            rotationInterval={2200}
                            splitBy="characters"
                            auto={true}
                            loop={true}
                          />
                        </span>
                      </motion.h1>
                      <p className="text-base sm:text-lg lg:text-xl text-gray-400 max-w-2xl mx-auto">
                        Win AI Search
                      </p>
                    </div>
                    
                    <div className="flex flex-col items-center justify-center space-y-2 mb-4">
                      <span className="text-xs uppercase text-gray-500 tracking-wider font-medium">Works with</span>
                      <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-gray-400">
                        <span className="flex items-center whitespace-nowrap">Google Gemini  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" className="ml-1"><path d="M2.52118 7.58241C2.52118 8.27634 1.9544 8.8432 1.26059 8.8432C0.566777 8.8432 0 8.27634 0 7.58241C0 6.88849 0.566777 6.32162 1.26059 6.32162H2.52118V7.58241Z" fill="#E21E5B"></path><path d="M3.15625 7.5825C3.15625 6.88858 3.72303 6.32172 4.41684 6.32172C5.11065 6.32172 5.67743 6.88858 5.67743 7.5825V10.7394C5.67743 11.4333 5.11065 12.0002 4.41684 12.0002C3.72303 12.0002 3.15625 11.4333 3.15625 10.7394V7.5825Z" fill="#E21E5B"></path><path d="M4.41684 2.52164C3.72303 2.52164 3.15625 1.95477 3.15625 1.26085C3.15625 0.566928 3.72303 6.10352e-05 4.41684 6.10352e-05C5.11065 6.10352e-05 5.67743 0.566928 5.67743 1.26085V2.52164H4.41684Z" fill="#36C6F0"></path><path d="M4.41695 3.15518C5.11076 3.15518 5.67754 3.72205 5.67754 4.41597C5.67754 5.10989 5.11076 5.67676 4.41695 5.67676H1.26059C0.566777 5.67676 0 5.10989 0 4.41597C0 3.72205 0.566777 3.15518 1.26059 3.15518H4.41695Z" fill="#36C6F0"></path><path d="M9.48047 4.41719C9.48047 3.72327 10.0472 3.1564 10.7411 3.1564C11.4349 3.1564 12.0016 3.72327 12.0016 4.41719C12.0016 5.11111 11.4349 5.67798 10.7411 5.67798H9.48047V4.41719Z" fill="#2EB77D"></path><path d="M8.8454 4.41765C8.8454 5.11157 8.27862 5.67844 7.58481 5.67844C6.89099 5.67844 6.32422 5.11157 6.32422 4.41765V1.26079C6.32422 0.566867 6.89099 0 7.58481 0C8.27862 0 8.8454 0.566867 8.8454 1.26079V4.41765Z" fill="#2EB77D"></path><path d="M7.58481 9.47812C8.27862 9.47812 8.8454 10.045 8.8454 10.7389C8.8454 11.4328 8.27862 11.9997 7.58481 11.9997C6.89099 11.9997 6.32422 11.4328 6.32422 10.7389V9.47812H7.58481Z" fill="#ECB22D"></path><path d="M7.58481 8.8432C6.89099 8.8432 6.32422 8.27634 6.32422 7.58241C6.32422 6.88849 6.89099 6.32162 7.58481 6.32162H10.7412C11.435 6.32162 12.0018 6.88849 12.0018 7.58241C12.0018 8.27634 11.435 8.8432 10.7412 8.8432H7.58481Z" fill="#ECB22D"></path></svg></span>
                        <span className="flex items-center whitespace-nowrap">OpenAI ChatGPT  <svg width="14" height="13" viewBox="0 0 14 13" fill="none" className="ml-1"><g clipPath="url(#clip0_2019_82286)"><path d="M9.66723 4.70923H13.1543C13.4838 4.70923 13.7508 4.97629 13.7508 5.30574V8.48201C13.7508 9.6928 12.7693 10.6743 11.5585 10.6743H11.5481C10.3373 10.6745 9.35564 9.69311 9.35547 8.48232C9.35547 8.48221 9.35547 8.48211 9.35547 8.482V5.02099C9.35547 4.84881 9.49505 4.70923 9.66723 4.70923Z" fill="#5059C9"></path><path d="M12.0222 4.08135C12.8024 4.08135 13.435 3.44882 13.435 2.66856C13.435 1.8883 12.8024 1.25577 12.0222 1.25577C11.2419 1.25577 10.6094 1.8883 10.6094 2.66856C10.6094 3.44882 11.2419 4.08135 12.0222 4.08135Z" fill="#5059C9"></path><path d="M7.62664 4.08134C8.75368 4.08134 9.66734 3.16769 9.66734 2.04064C9.66734 0.913591 8.75368 -6.10352e-05 7.62664 -6.10352e-05C6.49959 -6.10352e-05 5.58594 0.913591 5.58594 2.04064C5.58594 3.16769 6.49959 4.08134 7.62664 4.08134Z" fill="#7B83EB"></path><path d="M10.3481 4.70923H4.59208C4.26656 4.71728 4.00905 4.98743 4.0166 5.31296V8.93568C3.97114 10.8892 5.51666 12.5103 7.47009 12.5581C9.42353 12.5103 10.969 10.8892 10.9236 8.93568V5.31296C10.9311 4.98743 10.6736 4.71728 10.3481 4.70923Z" fill="#7B83EB"></path><path opacity="0.1" d="M7.78323 4.70923V9.78586C7.78167 10.0187 7.6406 10.2278 7.42533 10.3164C7.35679 10.3454 7.28312 10.3604 7.2087 10.3604H4.29207C4.25126 10.2568 4.21358 10.1532 4.18218 10.0464C4.07229 9.68619 4.01621 9.31169 4.01579 8.93504V5.31202C4.00824 4.98701 4.26532 4.71728 4.59032 4.70923H7.78323Z" fill="black"></path><path opacity="0.2" d="M7.46928 4.70923V10.0998C7.46927 10.1742 7.45432 10.2479 7.42533 10.3164C7.33669 10.5317 7.12755 10.6728 6.89475 10.6743H4.43963C4.38626 10.5707 4.33603 10.4671 4.29207 10.3604C4.24811 10.2536 4.21358 10.1532 4.18218 10.0464C4.07229 9.6862 4.01621 9.31169 4.01579 8.93504V5.31202C4.00824 4.98701 4.26532 4.71728 4.59032 4.70923H7.46928Z" fill="black"></path><path opacity="0.2" d="M7.46928 4.70923V9.47191C7.46688 9.78822 7.21106 10.044 6.89474 10.0464H4.18218C4.07229 9.68619 4.01621 9.31169 4.01579 8.93504V5.31202C4.00824 4.98701 4.26532 4.71728 4.59032 4.70923H7.46928Z" fill="black"></path><path opacity="0.2" d="M7.15532 4.70923V9.47191C7.15293 9.78822 6.8971 10.044 6.58079 10.0464H4.18218C4.07229 9.68619 4.01621 9.31169 4.01579 8.93504V5.31202C4.00824 4.98701 4.26532 4.71728 4.59032 4.70923H7.15532Z" fill="black"></path><path opacity="0.1" d="M7.7857 3.0861V4.07505C7.73232 4.07819 7.68209 4.08133 7.62872 4.08133C7.57535 4.08133 7.52512 4.07819 7.47174 4.07505C7.36577 4.06802 7.26067 4.0512 7.15779 4.02482C6.52203 3.87426 5.99679 3.42839 5.745 2.82552C5.70167 2.72428 5.66804 2.61915 5.64453 2.51157H7.21116C7.52797 2.51277 7.78449 2.76928 7.7857 3.0861Z" fill="black"></path><path opacity="0.2" d="M7.46893 3.40006V4.07506C7.36296 4.06803 7.25786 4.05122 7.15498 4.02483C6.51922 3.87427 5.99398 3.42841 5.74219 2.82553H6.8944C7.2112 2.82673 7.46772 3.08326 7.46893 3.40006Z" fill="black"></path><path opacity="0.2" d="M7.46893 3.40006V4.07506C7.36296 4.06803 7.25786 4.05122 7.15498 4.02483C6.51922 3.87427 5.99398 3.42841 5.74219 2.82553H6.8944C7.2112 2.82673 7.46772 3.08326 7.46893 3.40006Z" fill="black"></path><path opacity="0.2" d="M7.15498 3.40007V4.02483C6.51922 3.87427 5.99398 3.42841 5.74219 2.82553H6.58044C6.89725 2.82674 7.15377 3.08326 7.15498 3.40007Z" fill="black"></path><path d="M0.825474 2.82553H6.5815C6.89932 2.82553 7.15697 3.08318 7.15697 3.401V9.15703C7.15697 9.47485 6.89932 9.7325 6.5815 9.7325H0.825474C0.507646 9.7325 0.25 9.47485 0.25 9.15703V3.401C0.25 3.08318 0.507652 2.82553 0.825474 2.82553Z" fill="url(#paint0_linear_2019_82286)"></path><path d="M5.21652 5.01629H4.06588V8.14955H3.3328V5.01629H2.1875V4.40848H5.21652V5.01629Z" fill="white"></path></g><defs><linearGradient id="paint0_linear_2019_82286" x1="1.44988" y1="2.37586" x2="5.9571" y2="10.1822" gradientUnits="userSpaceOnUse"><stop stopColor="#5A62C3"></stop><stop offset="0.5" stopColor="#4D55BD"></stop><stop offset="1" stopColor="#3940AB"></stop></linearGradient><clipPath id="clip0_2019_82286"><rect width="13.5" height="12.5581" fill="white" transform="translate(0.25 -6.10352e-05)"></rect></clipPath></defs></svg></span>
                        {/* <span className="flex items-center whitespace-nowrap">  <svg width="14" height="12" viewBox="0 0 14 12" fill="none" className="ml-1"><path d="M11.6783 1.68101C10.8179 1.28619 9.89518 0.995304 8.93044 0.828702C8.91287 0.825486 8.89532 0.833522 8.88627 0.849593C8.76761 1.06066 8.63616 1.33601 8.54411 1.55243C7.50648 1.39708 6.47417 1.39708 5.45781 1.55243C5.36574 1.3312 5.22952 1.06066 5.11032 0.849593C5.10127 0.834058 5.08372 0.826023 5.06615 0.828702C4.10195 0.994772 3.17925 1.28566 2.31828 1.68101C2.31082 1.68422 2.30443 1.68959 2.30019 1.69655C0.550033 4.31133 0.0705905 6.86184 0.305789 9.38073C0.306853 9.39305 0.313771 9.40484 0.323349 9.41233C1.47805 10.2603 2.59659 10.7752 3.69434 11.1164C3.71191 11.1218 3.73053 11.1153 3.74171 11.1009C4.00138 10.7462 4.23286 10.3723 4.43133 9.9791C4.44304 9.95607 4.43186 9.92875 4.40792 9.91964C4.04076 9.78036 3.69115 9.61054 3.35485 9.41769C3.32825 9.40216 3.32612 9.36411 3.35059 9.34589C3.42136 9.29286 3.49215 9.23768 3.55972 9.18197C3.57195 9.17179 3.58899 9.16965 3.60336 9.17607C5.81272 10.1848 8.20462 10.1848 10.3879 9.17607C10.4023 9.16911 10.4193 9.17126 10.4321 9.18143C10.4997 9.23715 10.5704 9.29286 10.6417 9.34589C10.6662 9.36411 10.6646 9.40216 10.638 9.41769C10.3017 9.61428 9.95211 9.78036 9.58441 9.91911C9.56047 9.92822 9.54983 9.95607 9.56154 9.9791C9.76427 10.3718 9.99574 10.7457 10.2506 11.1003C10.2613 11.1153 10.2804 11.1218 10.298 11.1164C11.4011 10.7752 12.5196 10.2603 13.6743 9.41233C13.6844 9.40484 13.6908 9.39358 13.6919 9.38126C13.9734 6.46915 13.2204 3.93955 11.6959 1.69708C11.6921 1.68959 11.6858 1.68422 11.6783 1.68101ZM4.76126 7.84699C4.09609 7.84699 3.54801 7.23629 3.54801 6.4863C3.54801 5.7363 4.08546 5.12561 4.76126 5.12561C5.44237 5.12561 5.98514 5.74167 5.97449 6.4863C5.97449 7.23629 5.43704 7.84699 4.76126 7.84699ZM9.24705 7.84699C8.58189 7.84699 8.03381 7.23629 8.03381 6.4863C8.03381 5.7363 8.57125 5.12561 9.24705 5.12561C9.92817 5.12561 10.4709 5.74167 10.4603 6.4863C10.4603 7.23629 9.92817 7.84699 9.24705 7.84699Z" fill="#5865F2"></path></svg></span>
                        <span className="flex items-center whitespace-nowrap">Email  <svg width="16" height="14" viewBox="0 0 16 14" fill="none" className="ml-1"><path fillRule="evenodd" clipRule="evenodd" d="M0.5 7.00012C0.5 6.58591 0.835786 6.25012 1.25 6.25012H5.3C5.55076 6.25012 5.78494 6.37545 5.92404 6.5841L7.05139 8.27512H8.94861L10.076 6.5841C10.2151 6.37545 10.4492 6.25012 10.7 6.25012H14.75C15.1642 6.25012 15.5 6.58591 15.5 7.00012C15.5 7.41434 15.1642 7.75012 14.75 7.75012H11.1014L9.97404 9.44115C9.83494 9.6498 9.60076 9.77512 9.35 9.77512H6.65C6.39923 9.77512 6.16506 9.6498 6.02596 9.44115L4.89861 7.75012H1.25C0.835786 7.75012 0.5 7.41434 0.5 7.00012Z" fill="#9898A9"></path><path fillRule="evenodd" clipRule="evenodd" d="M4.787 0.849976L11.213 0.849976C11.6037 0.850183 11.987 0.959373 12.319 1.16527C12.6506 1.37092 12.9184 1.66491 13.0923 2.01424C13.0925 2.01465 13.0927 2.01506 13.0929 2.01548L15.4206 6.66418C15.4728 6.76842 15.5 6.88354 15.5 7.00012V11.05C15.5 11.6069 15.2787 12.1411 14.8849 12.5349C14.4911 12.9287 13.957 13.15 13.4 13.15H2.6C2.04304 13.15 1.5089 12.9287 1.11508 12.5349C0.721249 12.1411 0.5 11.6069 0.5 11.05V7.00012C0.5 6.88354 0.527177 6.76842 0.579374 6.66418L2.9071 2.01548C2.90728 2.01511 2.90747 2.01474 2.90765 2.01437C3.08152 1.66498 3.34932 1.37095 3.681 1.16527C4.01303 0.959373 4.39631 0.850183 4.787 0.849976ZM4.78726 2.34998C4.67568 2.35006 4.56634 2.38126 4.47151 2.44006C4.37665 2.49889 4.30007 2.58301 4.2504 2.68298L4.24938 2.68503L2 7.17726V11.05C2 11.2091 2.06321 11.3617 2.17574 11.4742C2.28826 11.5868 2.44087 11.65 2.6 11.65H13.4C13.5591 11.65 13.7117 11.5868 13.8243 11.4742C13.9368 11.3617 14 11.2091 14 11.05V7.17726L11.7506 2.68503L11.7496 2.68298C11.6999 2.58301 11.6234 2.49889 11.5285 2.44006C11.4337 2.38126 11.3243 2.35006 11.2127 2.34998H4.78726Z" fill="#9898A9"></path></svg></span>
                        <span className="flex items-center whitespace-nowrap">AND MORE</span> */}
                      </div>
                    </div>
                    
                    <motion.form
                      variants={formVariants}
                      initial="hidden"
                      animate="visible"
                      transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
                      className="flex flex-col sm:flex-row items-center justify-center gap-2 w-full max-w-md mx-auto mb-3"
                      onSubmit={(e: FormEvent<HTMLFormElement>) => e.preventDefault()}
                    >
                      <input
                        type="email"
                        placeholder="Your work email"
                        required
                        aria-label="Work Email"
                        className="flex-grow w-full sm:w-auto px-4 py-2 rounded-md bg-[#2a2a2a] border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0CF2A0] focus:border-transparent transition-all"
                      />
                      <motion.button
                        type="submit"
                        className="w-full sm:w-auto bg-[#0CF2A0] text-[#111111] px-5 py-2 rounded-md text-sm font-semibold hover:bg-opacity-90 transition-colors duration-200 whitespace-nowrap shadow-sm hover:shadow-md flex-shrink-0"
                        whileHover={{ scale: 1.03, y: -1 }}
                        whileTap={{ scale: 0.97 }}
                        transition={{ type: "spring", stiffness: 400, damping: 15 }}
                      >
                        Get Free Report (30s)
                      </motion.button>
                    </motion.form>
                  </motion.div>
                ) : step === "code" ? (
                  <motion.div 
                    key="code-step"
                    initial={{ opacity: 0, x: 100 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 100 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className="space-y-6 text-center"
                  >
                    <div className="space-y-1">
                      <h1 className="text-[2.5rem] font-bold leading-[1.1] tracking-tight text-white">We sent you a code</h1>
                      <p className="text-[1.25rem] text-white/50 font-light">Please enter it</p>
                    </div>
                    
                    <div className="w-full">
                      <div className="relative rounded-full py-4 px-5 border border-white/10 bg-transparent">
                        <div className="flex items-center justify-center">
                          {code.map((digit, i) => (
                            <div key={i} className="flex items-center">
                              <div className="relative">
                                <input
                                  ref={(el) => {
                                    codeInputRefs.current[i] = el;
                                  }}
                                  type="text"
                                  inputMode="numeric"
                                  pattern="[0-9]*"
                                  maxLength={1}
                                  value={digit}
                                  onChange={e => handleCodeChange(i, e.target.value)}
                                  onKeyDown={e => handleKeyDown(i, e)}
                                  className="w-8 text-center text-xl bg-transparent text-white border-none focus:outline-none focus:ring-0 appearance-none"
                                  style={{ caretColor: 'transparent' }}
                                />
                                {!digit && (
                                  <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center pointer-events-none">
                                    <span className="text-xl text-white">0</span>
                                  </div>
                                )}
                              </div>
                              {i < 5 && <span className="text-white/20 text-xl">|</span>}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <motion.p 
                        className="text-white/50 hover:text-white/70 transition-colors cursor-pointer text-sm"
                        whileHover={{ scale: 1.02 }}
                        transition={{ duration: 0.2 }}
                      >
                        Resend code
                      </motion.p>
                    </div>
                    
                    <div className="flex w-full gap-3">
                      <motion.button 
                        onClick={handleBackClick}
                        className="rounded-full bg-white text-black font-medium px-8 py-3 hover:bg-white/90 transition-colors w-[30%]"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        transition={{ duration: 0.2 }}
                      >
                        Back
                      </motion.button>
                      <motion.button 
                        className={`flex-1 rounded-full font-medium py-3 border transition-all duration-300 ${
                          code.every(d => d !== "") 
                          ? "bg-white text-black border-transparent hover:bg-white/90 cursor-pointer" 
                          : "bg-[#111] text-white/50 border-white/10 cursor-not-allowed"
                        }`}
                        disabled={!code.every(d => d !== "")}
                      >
                        Continue
                      </motion.button>
                    </div>
                    
                    <div className="pt-16">
                      <p className="text-xs text-white/40">
                        By signing up, you agree to the <Link href="#" className="underline text-white/40 hover:text-white/60 transition-colors">MSA</Link>, <Link href="#" className="underline text-white/40 hover:text-white/60 transition-colors">Product Terms</Link>, <Link href="#" className="underline text-white/40 hover:text-white/60 transition-colors">Policies</Link>, <Link href="#" className="underline text-white/40 hover:text-white/60 transition-colors">Privacy Notice</Link>, and <Link href="#" className="underline text-white/40 hover:text-white/60 transition-colors">Cookie Notice</Link>.
                      </p>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div 
                    key="success-step"
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, ease: "easeOut", delay: 0.3 }}
                    className="space-y-6 text-center"
                  >
                    <div className="space-y-1">
                      <h1 className="text-[2.5rem] font-bold leading-[1.1] tracking-tight text-white">You're in!</h1>
                      <p className="text-[1.25rem] text-white/50 font-light">Welcome</p>
                    </div>
                    
                    <motion.div 
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ duration: 0.5, delay: 0.5 }}
                      className="py-10"
                    >
                      <div className="mx-auto w-16 h-16 rounded-full bg-gradient-to-br from-white to-white/70 flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-black" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </motion.div>
                    
                    <motion.button 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 1 }}
                      className="w-full rounded-full bg-white text-black font-medium py-3 hover:bg-white/90 transition-colors"
                    >
                      Continue to Dashboard
                    </motion.button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default function HomePage() {
  return <SignInPage />;
}