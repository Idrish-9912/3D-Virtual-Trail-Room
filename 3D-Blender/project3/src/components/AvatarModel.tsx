import { useEffect, useRef, useState } from "react";
import { useGLTF } from "@react-three/drei";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import type { AvatarSettings } from "../types";

interface AvatarModelProps {
  settings: AvatarSettings;
}

/**
 * Loads the exported GLB avatar and applies live material color overrides
 * so the user can preview skin, hair, and clothing colors in the browser
 * without re-exporting from Blender.
 *
 * If the GLB file hasn't been generated yet, a friendly placeholder is shown.
 */
export default function AvatarModel({ settings }: AvatarModelProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [modelUrl, setModelUrl] = useState<string | null>(null);
  const [loadFailed, setLoadFailed] = useState(false);

  useEffect(() => {
    setLoadFailed(false);
    fetch("/avatar.glb")
      .then((res) => {
        if (!res.ok) throw new Error("not found");
        return res.blob();
      })
      .then((blob) => setModelUrl(URL.createObjectURL(blob)))
      .catch(() => setLoadFailed(true));
  }, []);

  if (loadFailed) {
    return <PlaceholderAvatar settings={settings} />;
  }

  if (!modelUrl) {
    return null;
  }

  return (
    <group ref={groupRef} position={[0, 0, 0]} dispose={null}>
      <SuspendedModel url={modelUrl} settings={settings} />
    </group>
  );
}

function SuspendedModel({ url, settings }: { url: string; settings: AvatarSettings }) {
  const { scene } = useGLTF(url) as THREE.GLTF & { scene: THREE.Group };
  const clone = useRef<THREE.Group | null>(null);

  if (!clone.current) {
    clone.current = scene.clone(true);
  }

  // Apply color overrides to materials by name.
  useEffect(() => {
    if (!clone.current) return;
    clone.current.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return;
      const mat = child.material as THREE.MeshStandardMaterial;
      if (!mat || !mat.name) return;

      if (mat.name === "M_Skin") mat.color.set(settings.skinColor);
      else if (mat.name === "M_Hair") mat.color.set(settings.hairColor);
      else if (mat.name === "M_TShirt" || mat.name === "M_Shirt" || mat.name === "M_Jacket")
        mat.color.set(settings.shirtColor);
      else if (mat.name === "M_Pants") mat.color.set(settings.pantsColor);
      else if (mat.name === "M_Shoes") mat.color.set(settings.shoeColor);

      mat.needsUpdate = true;
    });
  }, [settings]);

  return <primitive object={clone.current} scale={1} />;
}

/**
 * A simple stylized fallback avatar built from primitives so the viewer
 * works even before the Blender pipeline has exported a GLB.
 */
function PlaceholderAvatar({ settings }: { settings: AvatarSettings }) {
  return (
    <group position={[0, 0, 0]}>
      {/* Head */}
      <mesh position={[0, 1.52, 0]} castShadow>
        <sphereGeometry args={[0.13, 32, 32]} />
        <meshStandardMaterial color={settings.skinColor} roughness={0.5} />
      </mesh>
      {/* Hair cap */}
      <mesh position={[0, 1.56, 0]} castShadow>
        <sphereGeometry args={[0.135, 32, 32, 0, Math.PI * 2, 0, Math.PI * 0.55]} />
        <meshStandardMaterial color={settings.hairColor} roughness={0.7} />
      </mesh>
      {/* Eyes */}
      <mesh position={[0.045, 1.55, -0.11]}>
        <sphereGeometry args={[0.025, 16, 16]} />
        <meshStandardMaterial color={new THREE.Color(settings.hairColor).lerp(new THREE.Color("#ffffff"), 0.7)} roughness={0.2} />
      </mesh>
      <mesh position={[-0.045, 1.55, -0.11]}>
        <sphereGeometry args={[0.025, 16, 16]} />
        <meshStandardMaterial color={new THREE.Color(settings.hairColor).lerp(new THREE.Color("#ffffff"), 0.7)} roughness={0.2} />
      </mesh>
      {/* Torso (shirt) */}
      <mesh position={[0, 1.07, 0]} castShadow>
        <boxGeometry args={[0.22, 0.30, 0.13]} />
        <meshStandardMaterial color={settings.shirtColor} roughness={0.65} />
      </mesh>
      {/* Arms */}
      <mesh position={[0.28, 1.25, 0]} rotation={[0, 0, 0]} castShadow>
        <cylinderGeometry args={[0.045, 0.045, 0.26, 12]} />
        <meshStandardMaterial color={settings.skinColor} roughness={0.5} />
      </mesh>
      <mesh position={[-0.28, 1.25, 0]} rotation={[0, 0, 0]} castShadow>
        <cylinderGeometry args={[0.045, 0.045, 0.26, 12]} />
        <meshStandardMaterial color={settings.skinColor} roughness={0.5} />
      </mesh>
      {/* Legs (pants) */}
      <mesh position={[0.10, 0.69, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, 0.40, 12]} />
        <meshStandardMaterial color={settings.pantsColor} roughness={0.65} />
      </mesh>
      <mesh position={[-0.10, 0.69, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, 0.40, 12]} />
        <meshStandardMaterial color={settings.pantsColor} roughness={0.65} />
      </mesh>
      {/* Lower legs */}
      <mesh position={[0.10, 0.29, 0]} castShadow>
        <cylinderGeometry args={[0.05, 0.05, 0.40, 12]} />
        <meshStandardMaterial color={settings.pantsColor} roughness={0.65} />
      </mesh>
      <mesh position={[-0.10, 0.29, 0]} castShadow>
        <cylinderGeometry args={[0.05, 0.05, 0.40, 12]} />
        <meshStandardMaterial color={settings.pantsColor} roughness={0.65} />
      </mesh>
      {/* Shoes */}
      <mesh position={[0.10, 0.045, 0.06]} castShadow>
        <boxGeometry args={[0.085, 0.06, 0.18]} />
        <meshStandardMaterial color={settings.shoeColor} roughness={0.6} />
      </mesh>
      <mesh position={[-0.10, 0.045, 0.06]} castShadow>
        <boxGeometry args={[0.085, 0.06, 0.18]} />
        <meshStandardMaterial color={settings.shoeColor} roughness={0.6} />
      </mesh>
    </group>
  );
}

// Preload the GLB when it exists.
useGLTF.preload("/avatar.glb");
