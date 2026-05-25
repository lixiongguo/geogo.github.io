(function () {
	var PROJECTS = [
		{ id: "vector-field-decomposition", label: "向量场分解 · Vector Field Decomposition" },
		{ id: "discrete-exterior-calculus", label: "离散外微积分 · Discrete Exterior Calculus" },
		{ id: "simplicial-complex-operators", label: "单纯复形算子 · Simplicial Complex Operators" },
		{ id: "discrete-curvatures-and-normals", label: "离散曲率与法向 · Discrete Curvatures and Normals" },
		{ id: "poisson-problem", label: "Poisson 问题 · Poisson Problem" },
		{ id: "geodesic-distance", label: "测地距离 · Geodesic Distance" },
		{ id: "geometric-flow", label: "几何流 · Geometric Flow" },
		{ id: "parameterization", label: "曲面参数化 · Parameterization" },
		{ id: "direction-field-design", label: "方向场设计 · Direction Field Design" }
	];

	var wrap = document.getElementById("project-nav-wrap");
	if (!wrap) return;

	var current = wrap.getAttribute("data-current");
	if (!current) {
		var parts = location.pathname.replace(/\/+$/, "").split("/");
		current = parts[parts.length - 1] || "vector-field-decomposition";
	}

	var select = document.createElement("select");
	select.id = "project-nav-select";
	select.setAttribute("aria-label", "选择 DDG 练习项目");

	for (var i = 0; i < PROJECTS.length; i++) {
		var p = PROJECTS[i];
		var opt = document.createElement("option");
		opt.value = p.id;
		opt.textContent = p.label;
		if (p.id === current) opt.selected = true;
		select.appendChild(opt);
	}

	select.addEventListener("change", function () {
		var target = select.value;
		if (target && target !== current) {
			location.href = "../" + target + "/";
		}
	});

	wrap.appendChild(select);
})();
