# Getting Started with LBM-CHT

**Want to use it right now?** Follow these simple steps!

## ⚡ Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
cd /path/to/lbm-test-cht
pip install numpy scipy matplotlib pyyaml
```

That's it! The core dependencies are installed.

### Step 2: Verify Installation

```bash
python -c "from src.lattice import lattice_d3q19; print('✓ LBM-CHT is ready!')"
```

If you see "✓ LBM-CHT is ready!" - you're good to go!

### Step 3: Run Your First Simulation

```bash
python quick_start.py
```

This runs a simple channel flow simulation and shows you the results. It takes about 30-60 seconds.

## 🎯 What Can You Do Now?

### Option 1: Run Pre-Built Examples (Easiest)

We have 5 ready-to-run examples:

```bash
# 1. Simple channel flow (recommended first)
python examples/channel_flow.py

# 2. Lid-driven cavity
python examples/cavity_flow.py

# 3. Heated channel
python examples/heated_channel.py

# 4. Flow through gyroid structure
python examples/gyroid_flow.py

# 5. Full conjugate heat transfer (most advanced)
python examples/gyroid_cht.py
```

**Time**: Each takes 1-5 minutes to run. Results are saved in `output/` directory.

### Option 2: Write Your Own Simulation (Easy)

Create a file called `my_first_sim.py`:

```python
from src.flow_solver import FlowSolver
from src.geometry import GyroidGenerator
import numpy as np

# 1. Set up domain (start small!)
nx, ny, nz = 32, 32, 32
solver = FlowSolver(nx, ny, nz, viscosity=0.01)

# 2. Create geometry (simple channel)
geom = GyroidGenerator(nx, ny, nz)
solid_mask = geom.generate_channel(channel_height=24)
solver.set_solid_mask(solid_mask)

# 3. Add a driving force
force = np.zeros((nx, ny, nz, 3))
force[:, :, :, 0] = 0.0001  # Push fluid in x-direction
solver.set_external_force(force)

# 4. Run!
solver.initialize()
solver.run(n_steps=2000)

# 5. Get results
velocity = solver.u
print(f"Max velocity: {solver.get_velocity_magnitude().max():.6f}")
```

Run it:
```bash
python my_first_sim.py
```

### Option 3: Explore Interactively (Python Console)

```bash
python
```

Then try:

```python
# Import modules
from src.lattice import lattice_d3q19
from src.geometry import GyroidGenerator

# Check lattice
print(f"Using D3Q19 with {lattice_d3q19.Q} velocities")

# Generate a gyroid
geom = GyroidGenerator(32, 32, 32)
gyroid = geom.generate_gyroid(threshold=0.0, scale=1.0)
porosity = geom.calculate_porosity(gyroid)
print(f"Gyroid porosity: {porosity:.2%}")
```

## 🔧 Common Use Cases

### I want to simulate flow in a channel

```bash
python examples/channel_flow.py
```

Look at the output in `output/channel_Re*/` - you'll find:
- Velocity plots
- Comparison with analytical solution
- Error analysis

### I want to simulate heat transfer

```bash
python examples/heated_channel.py
```

This shows both flow and temperature fields.

### I want to use gyroid structures

```bash
python examples/gyroid_cht.py
```

This is the full conjugate heat transfer in gyroid geometry.

### I want to modify parameters

1. Copy an example: `cp examples/channel_flow.py my_sim.py`
2. Edit parameters at the top of the file
3. Run: `python my_sim.py`

## 📖 Where to Learn More

Depending on your goal:

| I want to... | Read this |
|--------------|-----------|
| Understand the theory | `README.md` (Theory Background section) |
| Learn step-by-step | `USER_GUIDE.md` |
| Install on my system | `INSTALL.md` |
| Modify the code | `CONTRIBUTING.md` |
| See technical details | `IMPLEMENTATION_SUMMARY.md` |

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'numpy'"

Install dependencies:
```bash
pip install numpy scipy matplotlib pyyaml
```

### Simulation is slow

Start with a smaller domain:
- Change `nx=ny=nz=32` (very fast)
- Then increase to 64 (moderate)
- Finally try 128+ (slow but detailed)

### Getting NaN values

Your simulation is unstable. Try:
- Reduce velocity/force: `force *= 0.1`
- Increase viscosity: `viscosity *= 2`
- Use smaller domain first

### Can't find output files

Results are saved in `output/` directory. If it doesn't exist:
```bash
mkdir output
```

## 💡 Pro Tips

1. **Start Small**: Always test with a 32³ domain first
2. **Check Examples**: Copy and modify existing examples
3. **Monitor Progress**: Examples print progress every 1000 steps
4. **Visualize**: Results are automatically plotted
5. **Read Errors**: Error messages usually tell you what's wrong

## 🎓 Learning Path

**Day 1**: Run `quick_start.py` and `examples/channel_flow.py`
- Understand basic flow simulation
- See how to set up geometry
- Learn about parameters

**Day 2**: Run `examples/heated_channel.py`
- Add temperature field
- Understand thermal properties
- See coupled simulation

**Day 3**: Run `examples/gyroid_cht.py`
- Complex geometry
- Full conjugate heat transfer
- Advanced analysis

**Week 1+**: Create your own simulations
- Modify parameters
- Try different geometries
- Explore advanced features

## ❓ FAQ

**Q: How long do simulations take?**
A: 32³ domain: ~10 seconds. 64³ domain: ~1-2 minutes. 128³ domain: ~10-30 minutes.

**Q: Can I run on GPU?**
A: Not yet, but CPU performance is good for research-scale problems.

**Q: What Reynolds numbers are supported?**
A: Up to Re~2000 with MRT collision (tested and validated).

**Q: Do I need to understand LBM theory?**
A: No! You can use the examples as templates. But reading the theory helps.

**Q: Can I modify the code?**
A: Yes! It's open source. See `CONTRIBUTING.md` for guidelines.

## 🆘 Still Stuck?

1. Check the example that's closest to what you want
2. Read the error message carefully
3. Try the simulation with smaller parameters
4. Look at `USER_GUIDE.md` for detailed tutorials
5. Open an issue on GitHub with:
   - What you're trying to do
   - What command you ran
   - The error message you got

## 🎉 Success!

If you've run an example successfully, you're ready to:
- Modify parameters for your needs
- Create custom geometries
- Analyze your results
- Share your findings

**Welcome to LBM-CHT! Happy simulating! 🚀**

---

**Next Steps:**
- Try all 5 examples: `ls examples/`
- Read `USER_GUIDE.md` for detailed tutorials
- Explore `config/simulation_config.yaml` for all options
- Check `README.md` for comprehensive documentation
