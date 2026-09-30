(() => {
  const pointerPosition = (control, event) => {
    const bounds = control.getBoundingClientRect();
    const x = ((event.clientX - bounds.left) / bounds.width) * 100;
    const y = ((event.clientY - bounds.top) / bounds.height) * 100;
    control.style.setProperty("--pointer-x", `${Math.max(0, Math.min(100, x))}%`);
    control.style.setProperty("--pointer-y", `${Math.max(0, Math.min(100, y))}%`);
  };

  document.querySelectorAll(".brand-action").forEach((control) => {
    control.addEventListener("pointermove", (event) => {
      if (event.pointerType === "mouse") pointerPosition(control, event);
    });
    control.addEventListener("pointerdown", (event) => {
      pointerPosition(control, event);
      control.classList.add("is-pressed");
    });
    ["pointerup", "pointercancel", "pointerleave"].forEach((type) => {
      control.addEventListener(type, () => control.classList.remove("is-pressed"));
    });
    control.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") control.classList.add("is-pressed");
    });
    control.addEventListener("keyup", () => control.classList.remove("is-pressed"));
  });
})();
