import test from 'node:test';
import assert from 'node:assert/strict';
import { stepTo, validWaypoint } from './motion.mjs';

test('constant speed: 2 units/second for 0.5 second travels 1 unit', () => {
  const result = stepTo([0, 0, 0], [3, 0, 0], 2, 0.5);
  assert.deepEqual(result.position, [1, 0, 0]);
  assert.equal(result.arrived, false);
});

test('snap to target when remaining distance is less than frame step', () => {
  const result = stepTo([0, 0, 0], [0.1, 0, 0], 2, 1);
  assert.deepEqual(result.position, [0.1, 0, 0]);
  assert.equal(result.arrived, true);
});

test('3D direction is normalized before multiplying speed', () => {
  const result = stepTo([0, 0, 0], [3, 0, 4], 2, 1);
  assert.ok(Math.abs(Math.hypot(...result.position) - 2) < 1e-12);
});

test('invalid speed and nonfinite inputs are rejected', () => {
  assert.equal(validWaypoint({x:1,y:0,z:1,speed:2}), true);
  assert.equal(validWaypoint({x:1,y:0,z:1,speed:0}), false);
  assert.equal(validWaypoint({x:Infinity,y:0,z:1,speed:2}), false);
});
