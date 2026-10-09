# Why the v3.1 Y-direction pushovers stop at about 0.3-0.5 % roof drift

Test case: B-REF pushed in Y.

- **Step size is not the cause.** The normal run (250 steps) stops at a roof drift of 0.36 %, base shear 5.7 % W. A 4x finer run (1000 steps, `B-REF_dir2_n1000.*`) stops at the same place: roof drift 0.37 %, base shear 5.8 % W.
- **The member strains are still tiny** in the step before the stop: pier axial strain about 3.5e-5, shear strain about 2e-4. The 1.7 m link beams each carry about 2,280 kN, which is their shear capacity.
- **The front core pier is losing its gravity compression.** The 1.7 m link beams act on the front pier (F) with coupling axial force. At storey 14 the pier's axial force falls from 40.6 MN (gravity) to 9.4 MN at step 37. The next step pushes the pier toward net tension. The whole wall section then cracks in tension at once (tension softening of Concrete02), and the solver cannot follow that sudden loss of stiffness, so the step is rejected as `numerical`.

The end of each Y pushover is therefore a physical event: **the front core pier reaching net tension (through-cracking)** under strong coupling by the deep link beams. It is the same in both models, because the walls and link beams are identical in both. It is not a peak strength. The curves are reported up to that point.
