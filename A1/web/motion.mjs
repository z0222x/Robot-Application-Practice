//运行计算模块

//方块下一步移动到哪里 
export function stepTo(current, target, speed, deltaSeconds) {
  const diff = target.map((value, i) => value - current[i]);
  const distance = Math.hypot(...diff);
  if (distance <= 1e-8) return { position: [...target], arrived: true };
  if (speed <= 0 || deltaSeconds <= 0) return { position: [...current], arrived: false };
  const step = speed * deltaSeconds;
  if (step >= distance) return { position: [...target], arrived: true };
  const ratio = step / distance;
  return {
    position: current.map((value, i) => value + diff[i] * ratio),
    arrived: false,
  };
}

//检查传来的坐标和速度是否合法
export function validWaypoint(point) {
  return point && ['x', 'y', 'z', 'speed'].every(k =>
    typeof point[k] === 'number' && Number.isFinite(point[k])) &&
    [point.x, point.y, point.z].every(v => Math.abs(v) <= 20) &&
    point.speed > 0 && point.speed <= 10;
}
