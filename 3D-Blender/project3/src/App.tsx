import { Suspense, useState } from "react";
import { Canvas } from "@react-three/fiber";
import {
  OrbitControls,
  Environment,
  ContactShadows,
  Html,
  useProgress,
} from "@react-three/drei";
import AvatarModel from "./components/AvatarModel";
import ControlPanel from "./components/ControlPanel";
import type { AvatarSettings } from "./types";

const defaultSettings: AvatarSettings = {
  skinColor: "#f4c8a8",
  hairColor: "#331f0f",
  shirtColor: "#4073b3",
  pantsColor: "#2e2e38",
  shoeColor: "#1f1f24",
  bodyType: "average",
  hairStyle: "short",
  faceShape: "oval",
};

function Loader() {
  const { progress } = useProgress();
  return (
    <Html center>
      <div style={{ color: "#fff", fontSize: "1.1rem" }}>
        Loading avatar… {progress.toFixed(0)}%
      </div>
    </Html>
  );
}

export default function App() {
  const [settings, setSettings] = useState<AvatarSettings>(defaultSettings);

  return (
    <div style={{ display: "flex", width: "100vw", height: "100vh" }}>
      {/* 3D viewport */}
      <div style={{ flex: 1, position: "relative" }}>
        <Canvas
          camera={{ position: [0, 1.2, 3.5], fov: 35 }}
          shadows
          gl={{ antialias: true }}
        >
          <ambientLight intensity={0.4} />
          <directionalLight
            position={[3, 5, 4]}
            intensity={1.2}
            castShadow
            shadow-mapSize={[2048, 2048]}
          />
          <Suspense fallback={<Loader />}>
            <AvatarModel settings={settings} />
            <Environment preset="studio" />
            <ContactShadows
              position={[0, 0, 0]}
              opacity={0.5}
              scale={3}
              blur={2.4}
              far={4}
            />
          </Suspense>
          <OrbitControls
            target={[0, 1, 0]}
            minDistance={1.5}
            maxDistance={6}
            minPolarAngle={0.2}
            maxPolarAngle={Math.PI / 1.8}
          />
        </Canvas>
      </div>

      {/* Side panel */}
      <ControlPanel settings={settings} onChange={setSettings} />
    </div>
  );
}
