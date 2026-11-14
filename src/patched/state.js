import snapshot from "./builder-profiles.json" with { type: "json" };

export function createState(frame = {}) {
  const profiles = {
    components: snapshot.components,
    loops: snapshot.loops,
    devices: snapshot.devices
  };

  return {
    getProfiles: () => profiles,
    setProfiles: async (key, value) => {
      profiles[key] = value;
    },
    updateFrame: async (details) => {
      Object.assign(frame, details);
    }
  };
}
