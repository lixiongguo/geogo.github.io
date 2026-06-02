/**
 * fish.js — Boid flocking fish for WebGL Water
 * 30 small fish swim in the pool, rendered as simple coloured meshes.
 */

function FishSchool() {
  this.fish = [];
  this.mesh  = null;   // shared fish body mesh
  this.shader = null;

  var N = 30;
  // rainbow palette
  var pal = [
    [1.0,0.3,0.3],[1.0,0.6,0.2],[1.0,1.0,0.2],
    [0.3,1.0,0.3],[0.3,0.6,1.0],[0.6,0.3,1.0]
  ];

  for (var i = 0; i < N; i++) {
    this.fish.push({
      pos:    new GL.Vector((Math.random()-0.5)*1.4, -0.5-Math.random()*0.4, (Math.random()-0.5)*1.4),
      vel:    new GL.Vector((Math.random()-0.5)*0.1, (Math.random()-0.5)*0.03, (Math.random()-0.5)*0.1),
      size:   0.02 + Math.random() * 0.02,
      color:  pal[i % pal.length],
      speed:  0.15 + Math.random() * 0.25
    });
  }
  this.buildMesh();
  this.buildShader();
}

// ---- shared fish mesh (simple body: 4 vertices → 2 triangles) ----
FishSchool.prototype.buildMesh = function() {
  this.mesh = new GL.Mesh({ coords: true, colors: true, vertices: true });
  // Fish body: diamond shape [-1,0] in XZ plane, nose at +x
  this.mesh.vertices.push([0.0, 0.0, 0.0]);   // tail centre
  this.mesh.vertices.push([1.0, 0.0, 0.0]);   // nose
  this.mesh.vertices.push([0.3, 0.0, 0.5]);   // top fin
  this.mesh.vertices.push([0.3, 0.0,-0.5]);   // bottom fin
  this.mesh.vertices.push([0.6, 0.0, 0.25]);  // body top
  this.mesh.vertices.push([0.6, 0.0,-0.25]);  // body bottom

  this.mesh.colors = [
    [1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1]
  ];
  // Triangles
  this.mesh.triangles = [
    [0,2,4], [0,4,3], [0,3,5], [0,5,2],    // body panels
    [1,4,2], [1,3,4], [1,5,3], [1,2,5]     // nose panels
  ];
  this.mesh.compile();

  // Tail fin
  this.tailMesh = new GL.Mesh({ coords: true, colors: true, vertices: true });
  this.tailMesh.vertices.push([-0.05, 0.0, 0.0]);
  this.tailMesh.vertices.push([-0.35, 0.0, 0.45]);
  this.tailMesh.vertices.push([-0.35, 0.0,-0.45]);
  this.tailMesh.colors = [[1,1,1,1],[1,1,1,1],[1,1,1,1]];
  this.tailMesh.triangles = [[0,1,2]];
  this.tailMesh.compile();
};

// ---- shader: simple vertex colour ----
FishSchool.prototype.buildShader = function() {
  this.shader = new GL.Shader('\
    uniform vec4 fishColor;\
    void main() {\
      gl_Position = gl_ModelViewProjectionMatrix * vec4(gl_Vertex.xyz, 1.0);\
      gl_FrontColor = fishColor;\
    }\
  ', '\
    void main() {\
      gl_FragColor = gl_Color;\
    }\
  ');
};

// ---- Boid update ----
FishSchool.prototype.update = function(dt) {
  if (dt > 0.2) dt = 0.2;   // clamp long frames
  var fish = this.fish;
  var n = fish.length;

  // Avoid computing O(n²) per frame by grouping
  for (var i = 0; i < n; i++) {
    var f = fish[i];
    var steerSep = new GL.Vector();
    var steerAli = new GL.Vector();
    var steerCoh = new GL.Vector();
    var steerBnd = new GL.Vector();
    var neighbourSep = 0, neighbourAli = 0, neighbourCoh = 0;

    for (var j = 0; j < n; j++) {
      if (i === j) continue;
      var g = fish[j];
      var d = f.pos.distance(g.pos);
      if (d < 0.001) continue;

      // Separation (close range)
      if (d < 0.06) {
        steerSep = steerSep.add(f.pos.subtract(g.pos).divide(d * d));
        neighbourSep++;
      }
      // Alignment + Cohesion (medium range)
      if (d < 0.25) {
        steerAli = steerAli.add(g.vel);
        steerCoh = steerCoh.add(g.pos);
        neighbourAli++;
      }
    }

    // Normalise steering
    if (neighbourSep > 0) f.vel = f.vel.add(steerSep.multiply(0.03));
    if (neighbourAli > 0) {
      steerAli = steerAli.divide(neighbourAli);
      f.vel = f.vel.add(steerAli.subtract(f.vel).multiply(0.02));
    }
    if (neighbourCoh > 0) {
      steerCoh = steerCoh.divide(neighbourCoh);
      f.vel = f.vel.add(steerCoh.subtract(f.pos).multiply(0.01));
    }

    // Boundary: stay inside pool
    var strength = 0.15;
    if (f.pos.x < -0.75) f.vel.x += strength;
    if (f.pos.x >  0.75) f.vel.x -= strength;
    if (f.pos.z < -0.75) f.vel.z += strength;
    if (f.pos.z >  0.75) f.vel.z -= strength;
    // Stay submerged (don't fly out)
    if (f.pos.y > -0.15) f.vel.y -= 0.03;
    if (f.pos.y < -0.85) f.vel.y += 0.03;

    // Speed regulation
    var spd = f.vel.length();
    if (spd > f.speed) f.vel = f.vel.multiply(f.speed / spd);
    if (spd < f.speed * 0.3) f.vel = f.vel.normalize().multiply(f.speed * 0.3);

    // Update position
    f.pos = f.pos.add(f.vel.multiply(dt));
  }
};

// ---- Render ----
FishSchool.prototype.render = function() {
  var shader = this.shader;
  var fish = this.fish;
  // Use QUADS-like triangles — body + tail drawn per fish
  for (var i = 0; i < fish.length; i++) {
    var f = fish[i];
    gl.pushMatrix();
    gl.translate(f.pos.x, f.pos.y, f.pos.z);

    // Point nose in velocity direction
    var v = f.vel.unit();
    var yaw = Math.atan2(v.z, v.x);
    gl.rotate(yaw * 180 / Math.PI, 0, -1, 0);

    var s = f.size;
    gl.scale(s, s, s);

    shader.uniforms({ fishColor: f.color.concat(1) });
    shader.draw(this.mesh, gl.TRIANGLES);
    shader.draw(this.tailMesh, gl.TRIANGLES);

    gl.popMatrix();
  }
};
