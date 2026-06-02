/**
 * fish.js — Boid flocking fish for WebGL Water
 * 20 colourful fish swim just below the surface, rendered as simple triangles.
 */
function FishSchool() {
  this.fish = [];
  this.bodyMesh = null;
  this.tailMesh = null;
  this.shader = null;

  var N = 20;
  var pal = [
    [1.0,0.2,0.2],[1.0,0.5,0.1],[1.0,0.9,0.1],
    [0.2,1.0,0.2],[0.1,0.7,1.0],[0.6,0.2,1.0]
  ];

  for (var i = 0; i < N; i++) {
    var ang = Math.random() * Math.PI * 2;
    this.fish.push({
      pos:   new GL.Vector(Math.cos(ang)*0.6, -0.15-Math.random()*0.3, Math.sin(ang)*0.6),
      vel:   new GL.Vector((Math.random()-0.5)*0.15, 0, (Math.random()-0.5)*0.15),
      size:  0.12 + Math.random() * 0.1,
      color: pal[i % pal.length],
      speed: 0.2 + Math.random() * 0.3
    });
  }
  this.buildMeshes();
  this.buildShader();
}

// ---- flat fish body (diamond in XZ plane, nose at +X) ----
FishSchool.prototype.buildMeshes = function() {
  this.bodyMesh = new GL.Mesh({ coords: true, vertices: true });
  this.bodyMesh.vertices = [
    [0.0, 0, 0],       // tail
    [1.0, 0, 0],       // nose
    [0.35, 0, 0.55],   // top fin tip
    [0.35, 0,-0.55],   // bottom fin tip
  ];
  this.bodyMesh.triangles = [[0,1,2],[0,3,1],[0,2,3]];
  this.bodyMesh.compile();

  this.tailMesh = new GL.Mesh({ coords: true, vertices: true });
  this.tailMesh.vertices = [
    [-0.1, 0, 0],
    [-0.5, 0, 0.45],
    [-0.5, 0,-0.45]
  ];
  this.tailMesh.triangles = [[0,1,2]];
  this.tailMesh.compile();
};

// ---- shader: flat colour via uniform ----
FishSchool.prototype.buildShader = function() {
  this.shader = new GL.Shader('\
    uniform vec4 fishColor;\
    varying vec4 vC;\
    void main() {\
      gl_Position = gl_ModelViewProjectionMatrix * vec4(gl_Vertex.xyz, 1.0);\
      vC = fishColor;\
    }\
  ', '\
    varying vec4 vC;\
    void main() {\
      gl_FragColor = vC;\
    }\
  ');
};

// ---- Boid update ----
FishSchool.prototype.update = function(dt) {
  if (dt > 0.3) dt = 0.3;
  var fish = this.fish, n = fish.length;

  for (var i = 0; i < n; i++) {
    var f = fish[i];
    var sep = new GL.Vector(), ali = new GL.Vector(), coh = new GL.Vector();
    var nSep = 0, nAli = 0;

    for (var j = 0; j < n; j++) {
      if (i === j) continue;
      var g = fish[j];
      var d = f.pos.distance(g.pos);
      if (d < 1e-6) continue;

      if (d < 0.18) {  // separation range
        var away = f.pos.subtract(g.pos);
        sep = sep.add(away.divide(d * d));
        nSep++;
      }
      if (d < 0.5) {   // alignment + cohesion range
        ali = ali.add(g.vel);
        coh = coh.add(g.pos);
        nAli++;
      }
    }

    if (nSep  > 0) f.vel = f.vel.add(sep.multiply(0.05));
    if (nAli  > 0) {
      ali = ali.divide(nAli);
      f.vel = f.vel.add(ali.subtract(f.vel).multiply(0.03));
      coh = coh.divide(nAli);
      f.vel = f.vel.add(coh.subtract(f.pos).multiply(0.015));
    }

    // Boundaries — stay in pool + near surface
    var s = 0.2;
    if (f.pos.x < -0.8) f.vel.x += s;
    if (f.pos.x >  0.8) f.vel.x -= s;
    if (f.pos.z < -0.8) f.vel.z += s;
    if (f.pos.z >  0.8) f.vel.z -= s;
    if (f.pos.y > -0.05) f.vel.y -= 0.05;  // don't breach surface
    if (f.pos.y < -0.6)  f.vel.y += 0.04;  // don't sink too deep

    // Speed
    var spd = f.vel.length();
    if (spd < 1e-6) {
      var a = Math.random() * Math.PI * 2;
      f.vel = new GL.Vector(Math.cos(a), 0, Math.sin(a)).multiply(f.speed);
    } else if (spd > f.speed) {
      f.vel = f.vel.multiply(f.speed / spd);
    }

    f.pos = f.pos.add(f.vel.multiply(dt));
  }
};

// ---- Render ----
FishSchool.prototype.render = function() {
  var shader = this.shader;
  for (var i = 0; i < this.fish.length; i++) {
    var f = this.fish[i];
    gl.pushMatrix();
    gl.translate(f.pos.x, f.pos.y, f.pos.z);

    // Orient toward velocity
    var v = f.vel.unit();
    var yaw = Math.atan2(v.z, v.x) * 180 / Math.PI;
    gl.rotate(yaw, 0, -1, 0);

    var s = f.size;
    gl.scale(s, s, s);

    shader.uniforms({ fishColor: f.color.concat(1) });
    shader.draw(this.bodyMesh, gl.TRIANGLES);
    shader.draw(this.tailMesh, gl.TRIANGLES);

    gl.popMatrix();
  }
};
