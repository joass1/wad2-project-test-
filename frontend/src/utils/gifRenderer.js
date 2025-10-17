export class GifRenderer {
  constructor() {
    this.gifCache = new Map();
  }

  async loadGif(url) {
    if (this.gifCache.has(url)) {
      return this.gifCache.get(url);
    }

    return new Promise((resolve, reject) => {
      if (typeof gifler === 'undefined') {
        // Fallback to static image
        const img = new Image();
        img.onload = () => resolve({ image: img, isAnimated: false });
        img.onerror = reject;
        img.src = url;
        return;
      }

      const canvas = document.createElement('canvas');
      const animator = gifler(url);
      
      animator.frames(canvas, (ctx, frame) => {
        canvas.width = frame.width;
        canvas.height = frame.height;
        ctx.drawImage(frame.buffer, 0, 0);
      });

      animator.load(() => {
        this.gifCache.set(url, { canvas, isAnimated: true });
        resolve({ canvas, isAnimated: true });
      });
    });
  }

  render(ctx, gifData, x, y, width, height) {
    if (gifData.isAnimated && gifData.canvas) {
      ctx.drawImage(gifData.canvas, x, y, width, height);
    } else if (gifData.image) {
      ctx.drawImage(gifData.image, x, y, width, height);
    }
  }
}
