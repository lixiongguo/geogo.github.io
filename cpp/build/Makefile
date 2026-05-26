############################################################################
# WASM Makefile for uv_unwrap_simple only
# Usage (from cpp/build):
#   make uv_unwrap_simple
#   make clean
############################################################################

EMXX ?= em++

SRC_ROOT ?= ../conformal-parameterization
OUT_DIR ?= ../../assets/wasm
BUILD_DIR ?= build

EIGEN_INC ?= ../deps/eigen-3.4.0
GLM_INC ?= ../deps/glm
MOSEK_INC ?= ../deps/mosek

CXXFLAGS_COMMON := -std=c++17 -O2 -flto
INC_FLAGS := -I$(SRC_ROOT) \
             -I$(SRC_ROOT)/uv_unwrap_simple \
             -I$(EIGEN_INC) -I$(GLM_INC)

MESH_SRCS := $(SRC_ROOT)/Mesh.cpp \
             $(SRC_ROOT)/MeshIO.cpp \
             $(SRC_ROOT)/Parameterization.cpp \
             $(SRC_ROOT)/Vertex.cpp \
             $(SRC_ROOT)/Edge.cpp \
             $(SRC_ROOT)/Face.cpp \
             $(SRC_ROOT)/HalfEdge.cpp

UV_SIMPLE_SRCS := uv-unwrap-simple/wasm_uv_unwrap_simple.cpp \
                  $(SRC_ROOT)/uv_unwrap_simple/Lscm.cpp \
                  $(SRC_ROOT)/uv_unwrap_simple/Tutte.cpp \
                  $(SRC_ROOT)/uv_unwrap_simple/Scp.cpp \
                  $(SRC_ROOT)/QcError.cpp \
                  $(MESH_SRCS)

UV_SIMPLE_OUT := $(OUT_DIR)/uv_unwrap_simple.js
UV_SIMPLE_EXPORT := UvUnwrapSimpleSolver

.PHONY: all uv_unwrap_simple simple clean help

all: uv_unwrap_simple

simple: uv_unwrap_simple

help:
	@echo "Targets:"
	@echo "  uv_unwrap_simple  Build Tutte / LSCM / SCP WASM only"
	@echo "  clean             Remove uv_unwrap_simple outputs and temp files"

uv_unwrap_simple: $(UV_SIMPLE_OUT)

$(UV_SIMPLE_OUT): $(UV_SIMPLE_SRCS)
	@mkdir -p $(OUT_DIR) $(BUILD_DIR)
	@printf '["_malloc","_free","_solve_lscm","_solve_tutte_circle","_solve_tutte_square","_solve_scp","_get_uv_result","_get_uv_result_size","_get_last_time_ms","_dispose","_load_mesh_with_uv","_compute_qc_error","_get_qc_errors","_get_qc_errors_size","_get_qc_colors","_get_qc_colors_size"]\n' > $(BUILD_DIR)/uv_unwrap_simple.efile
	$(EMXX) $(CXXFLAGS_COMMON) $(INC_FLAGS) \
	  -s MODULARIZE=1 -s EXPORT_NAME="$(UV_SIMPLE_EXPORT)" \
	  -s ALLOW_MEMORY_GROWTH=1 -s INITIAL_MEMORY=268435456 -s WASM=1 \
	  -s "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','UTF8ToString','getValue','setValue']" \
	  -s EXPORTED_FUNCTIONS=@$(BUILD_DIR)/uv_unwrap_simple.efile \
	  -s FORCE_FILESYSTEM=0 -s ENVIRONMENT='web' \
	  $(UV_SIMPLE_SRCS) -o $@
	@echo "[DONE] uv_unwrap_simple -> $@"

clean:
	@rm -rf $(BUILD_DIR)
	@rm -f $(OUT_DIR)/uv_unwrap_simple.js $(OUT_DIR)/uv_unwrap_simple.wasm
	@echo "[DONE] Clean complete."
