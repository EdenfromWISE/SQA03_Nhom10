import { useEffect, useRef } from "react";

// SFX: preload bằng Web Audio API để giảm độ trễ
const useSfx = () => {
  const ctxRef = useRef(null);
  const buffersRef = useRef({});
  const unlockedRef = useRef(false);

  const ensureCtx = () => {
    if (!ctxRef.current) ctxRef.current = new (window.AudioContext || window.webkitAudioContext)();
    return ctxRef.current;
  };

  const loadBuffer = async (url, key) => {
    try {
      const ctx = ensureCtx();
      const res = await fetch(url, { cache: 'force-cache' });
      const arr = await res.arrayBuffer();
      const buf = await ctx.decodeAudioData(arr);
      buffersRef.current[key] = buf;
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    loadBuffer('/sfx/Click.mp3', 'click');
    loadBuffer('/sfx/Correct.mp3', 'ok');
    loadBuffer('/sfx/Wrong.mp3', 'wrong');

    const unlock = () => {
      const ctx = ensureCtx();
      if (ctx.state === 'suspended') ctx.resume();
      unlockedRef.current = true;
      window.removeEventListener('pointerdown', unlock, { capture: true });
    };
    window.addEventListener('pointerdown', unlock, { capture: true, once: true });
    return () => window.removeEventListener('pointerdown', unlock, { capture: true });
  }, []);

  const playBuffer = (key, volume = 0.5) => {
    const ctx = ensureCtx();
    const buf = buffersRef.current[key];
    if (!buf) return;
    const src = ctx.createBufferSource();
    const gain = ctx.createGain();
    src.buffer = buf;
    gain.gain.value = volume;
    src.connect(gain);
    gain.connect(ctx.destination);
    src.start();
  };

  return {
    playClick: () => playBuffer('click', 0.4),
    playCorrect: () => playBuffer('ok', 0.5),
    playWrong: () => playBuffer('wrong', 0.5),
  };
};

export default useSfx;

