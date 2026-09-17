import type { AvatarSettings } from "../types";

interface ControlPanelProps {
  settings: AvatarSettings;
  onChange: (settings: AvatarSettings) => void;
}

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: "0.85rem",
  fontWeight: 600,
  marginBottom: "0.25rem",
  color: "#c0c0d0",
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: "0.75rem",
  fontWeight: 700,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  color: "#8a8aa0",
  margin: "1.25rem 0 0.5rem",
  paddingBottom: "0.25rem",
  borderBottom: "1px solid #2a2a44",
};

const controlRowStyle: React.CSSProperties = {
  marginBottom: "0.75rem",
};

const selectStyle: React.CSSProperties = {
  width: "100%",
  padding: "0.4rem 0.5rem",
  borderRadius: "6px",
  border: "1px solid #3a3a55",
  background: "#252540",
  color: "#e0e0e0",
  fontSize: "0.85rem",
  cursor: "pointer",
};

const colorInputStyle: React.CSSProperties = {
  width: "100%",
  height: "36px",
  borderRadius: "6px",
  border: "1px solid #3a3a55",
  background: "none",
  cursor: "pointer",
};

const panelStyle: React.CSSProperties = {
  width: "320px",
  height: "100%",
  background: "#161629",
  borderLeft: "1px solid #2a2a44",
  padding: "1.5rem 1.25rem",
  overflowY: "auto",
  boxShadow: "-4px 0 24px rgba(0,0,0,0.3)",
};

const titleStyle: React.CSSProperties = {
  fontSize: "1.25rem",
  fontWeight: 700,
  marginBottom: "0.25rem",
  color: "#fff",
};

const subtitleStyle: React.CSSProperties = {
  fontSize: "0.8rem",
  color: "#8a8aa0",
  marginBottom: "1rem",
};

export default function ControlPanel({ settings, onChange }: ControlPanelProps) {
  const update = <K extends keyof AvatarSettings>(key: K, value: AvatarSettings[K]) => {
    onChange({ ...settings, [key]: value });
  };

  return (
    <div style={panelStyle}>
      <h1 style={titleStyle}>Avatar Studio</h1>
      <p style={subtitleStyle}>Customize your 3D avatar</p>

      {/* Colors */}
      <div style={sectionTitleStyle}>Colors</div>

      <div style={controlRowStyle}>
        <label style={labelStyle}>Skin</label>
        <input
          type="color"
          style={colorInputStyle}
          value={settings.skinColor}
          onChange={(e) => update("skinColor", e.target.value)}
        />
      </div>

      <div style={controlRowStyle}>
        <label style={labelStyle}>Hair</label>
        <input
          type="color"
          style={colorInputStyle}
          value={settings.hairColor}
          onChange={(e) => update("hairColor", e.target.value)}
        />
      </div>

      <div style={controlRowStyle}>
        <label style={labelStyle}>Shirt</label>
        <input
          type="color"
          style={colorInputStyle}
          value={settings.shirtColor}
          onChange={(e) => update("shirtColor", e.target.value)}
        />
      </div>

      <div style={controlRowStyle}>
        <label style={labelStyle}>Pants</label>
        <input
          type="color"
          style={colorInputStyle}
          value={settings.pantsColor}
          onChange={(e) => update("pantsColor", e.target.value)}
        />
      </div>

      <div style={controlRowStyle}>
        <label style={labelStyle}>Shoes</label>
        <input
          type="color"
          style={colorInputStyle}
          value={settings.shoeColor}
          onChange={(e) => update("shoeColor", e.target.value)}
        />
      </div>

      {/* Body & Face */}
      <div style={sectionTitleStyle}>Body & Face</div>

      <div style={controlRowStyle}>
        <label style={labelStyle}>Body Type</label>
        <select
          style={selectStyle}
          value={settings.bodyType}
          onChange={(e) => update("bodyType", e.target.value as AvatarSettings["bodyType"])}
        >
          <option value="slim">Slim</option>
          <option value="average">Average</option>
          <option value="athletic">Athletic</option>
        </select>
      </div>

      <div style={controlRowStyle}>
        <label style={labelStyle}>Hair Style</label>
        <select
          style={selectStyle}
          value={settings.hairStyle}
          onChange={(e) => update("hairStyle", e.target.value as AvatarSettings["hairStyle"])}
        >
          <option value="short">Short</option>
          <option value="medium">Medium</option>
          <option value="long">Long</option>
          <option value="buzz">Buzz</option>
          <option value="bob">Bob</option>
        </select>
      </div>

      <div style={controlRowStyle}>
        <label style={labelStyle}>Face Shape</label>
        <select
          style={selectStyle}
          value={settings.faceShape}
          onChange={(e) => update("faceShape", e.target.value as AvatarSettings["faceShape"])}
        >
          <option value="oval">Oval</option>
          <option value="round">Round</option>
          <option value="square">Square</option>
          <option value="heart">Heart</option>
        </select>
      </div>
    </div>
  );
}
