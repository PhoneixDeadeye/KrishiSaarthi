import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Text } from '@react-three/drei';
import * as THREE from 'three';

// Basic Farm Plot component representing a "Field" in 3D space
const FarmPlot = ({ position, color, name, healthScore, onClick }: any) => {
  const mesh = useRef<THREE.Mesh>(null);
  const [hovered, setHover] = useState(false);

  // Animate a gentle breathing effect
  useFrame((state) => {
    if (mesh.current) {
        mesh.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2 + position[0]) * 0.1;
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={mesh}
        onClick={(e) => { e.stopPropagation(); onClick(); }}
        onPointerOver={(e) => { e.stopPropagation(); setHover(true); }}
        onPointerOut={(e) => setHover(false)}
      >
        <boxGeometry args={[4, 0.5, 4]} />
        <meshStandardMaterial color={hovered ? 'hotpink' : color} roughness={0.8} />
      </mesh>
      
      {/* Floating UI Label for the Field */}
      <Text
        position={[0, 2, 0]}
        fontSize={0.5}
        color="white"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.05}
        outlineColor="black"
      >
        {name}
      </Text>
      {healthScore !== undefined && (
        <Text
          position={[0, 1.3, 0]}
          fontSize={0.3}
          color={healthScore > 80 ? '#4ade80' : '#f87171'}
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.05}
          outlineColor="black"
        >
          Temp: {healthScore}°C
        </Text>
      )}
    </group>
  );
};

export const FarmMap3D: React.FC<{ fields: any[], onFieldClick: (fieldId: string) => void }> = ({ fields, onFieldClick }) => {
  return (
    <div className="w-full h-[500px] rounded-xl overflow-hidden shadow-2xl border border-border bg-slate-900">
      <Canvas camera={{ position: [0, 8, 12], fov: 50 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 20, 5]} intensity={1.5} castShadow />
        <pointLight position={[-10, 10, -10]} intensity={0.5} color="blue" />
        
        {/* Environment setup */}
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        <fog attach="fog" args={['#0f172a', 10, 30]} />
        
        {/* Render dynamically passed fields — no data shown if empty */}
        {fields.length > 0 ? (
          fields.map((f, i) => (
            <FarmPlot
              key={f.id}
              position={[(i % 3) * 6 - 5, 0, Math.floor(i / 3) * 6 - 5]}
              color={f.risk_score > 0.5 ? '#f59e0b' : '#22c55e'}
              name={f.name || `Field ${i+1}`}
              healthScore={f.temperature}
              onClick={() => onFieldClick(f.id)}
            />
          ))
        ) : (
          <Text
            position={[0, 2, 0]}
            fontSize={0.6}
            color="#94a3b8"
            anchorX="center"
            anchorY="middle"
            outlineWidth={0.05}
            outlineColor="black"
          >
            No fields added yet
          </Text>
        )}

        {/* Floor grid for depth */}
        <gridHelper args={[50, 50, '#1e293b', '#0f172a']} position={[0, -0.25, 0]} />
        
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          maxPolarAngle={Math.PI / 2 - 0.1} // Prevent going under the floor
          minDistance={5}
          maxDistance={25}
        />
      </Canvas>
    </div>
  );
};
