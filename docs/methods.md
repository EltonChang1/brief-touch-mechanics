# Brief-Touch Mechanics: Methods and Research Review

**Reviewed: 10 October 2026; status updated: 12 October 2026. The force-pilot software and HaTT access/schema audit are implemented; calibration and timing remain unverified. No real force-prediction, motion or robot-task result is claimed.**

This document supports the [concise project report](../README.md). Published findings below are distinguished from our design choices. The proposed protocol refines the existing [Stage B/C plan](https://github.com/EltonChang1/tactile-contact-research/blob/c6fee1245a86bd45c3a6bcbe16c838e1b4a4c5d9/docs/research_plan.md) and [implementation guide](https://github.com/EltonChang1/tactile-contact-research/blob/c6fee1245a86bd45c3a6bcbe16c838e1b4a4c5d9/docs/implementation_guide.md). The [execution report](execution-report.md) records the implemented software, synthetic checks and bounded real-data audit; physical collection and validation remain pending.

The [execution plan](experiment-plan.md) turns this review into a staged protocol with a primary baseline, trial allocations, draft practical thresholds and a schedule. Its targets remain provisional until measurement/pilot checks and must be frozen before held-out confirmation.

## 1. The question and the claim

After a limited support touch on a new surface, predict forces in independent later slides and, subsequently, the motion of a body with the same contact pad.

There are three separate hypotheses:

1. **Contact adaptation:** brief measured-force calibration improves on a global friction setting.
2. **Tactile information:** tactile observations improve predictions under a declared measurement interface.
3. **Dynamics utility:** contact estimates improve real forward-motion prediction and eventually a specific task.

An advantage at one stage does not establish the later stages. A successful simple force fit can support useful contact adaptation even if AI adds no benefit.

The first model describes effective friction for a specified probe/pad–surface pair, tested speed/load range and preparation. NIST treats friction as dependent on the interacting bodies, environment and contact conditions. Record both materials, geometry, mounting, surface preparation and environmental conditions. Transfer to another object's underside needs its own test. [NIST SP 960-11, section 6.3.2.6](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication960-11.pdf).

## 2. What related work establishes

| Primary source | Relevant evidence | Boundary for our design |
| --- | --- | --- |
| [How Much Haptic Surface Data Is Enough? — Burka and Kuchenbecker, 2017](https://www.cs.utexas.edu/~jsinapov/AAAI-SSS-2017/paper/Burka_AAAI_SSS_2017.pdf) | Online Coulomb-plus-viscous fitting from measured force and speed; studies when parameters stabilize. | One vinyl surface and a 120-second exploration. Its 55.4-second stopping result is particular to that setup and criterion. It does not establish our proposed brief budget or unseen-surface accuracy. |
| [DiffTactile — ICLR 2024](https://arxiv.org/html/2403.08716v1) | Fits contact/sensor parameters using real force and tactile-marker measurements; tests other interaction types. | Real identification uses acrylic and tape, with 10 seconds pressing plus 10 seconds sliding/twisting. The identification table scores marker error. It does not validate half-second vibration-only force inference. |
| [TacTID — IEEE Sensors Journal 2024](https://charon-bo.github.io/assets/PDF/TacTID.pdf) | Estimates sliding friction from calibrated tactile force estimates, checked against an independent force sensor; also studies effective stiffness. | Verified sliding and a long sliding trajectory are important. It does not show that one short slide identifies every mechanical parameter. |
| [RoboPack — RSS 2024](https://www.roboticsproceedings.org/rss20/p130.html), [full paper](https://arxiv.org/html/2407.01418v1) | Tactile-informed dynamics, motion prediction and real pushing/packing, with tactile ablations and a fitted physics baseline. | Task training and continuing tactile history differ from our brief calibration. The physics baseline's restricted inputs and capacity matter when interpreting its comparison. |
| [Predictive Visuo-Tactile Interactive Perception — TRO 2025 preprint](https://arxiv.org/html/2411.09020v1) | Active pushing/pulling, property inference and goal-directed control; evaluates held-out object configurations. | Uses repeated five-second actions and predominantly quasi-static planar interactions. We will independently define sliding ground truth and parameter observability. |
| [Visuo-Tactile World Models — February 2026 preprint](https://arxiv.org/html/2602.06001v1) | Reports improved contact-aware predictions and real robot planning with tactile inputs. | Appendix E limits evaluation to trajectories within training tasks and planning in the same scenes/objects. Our proposed complete-surface holdout asks a different generalization question. |

These are precedents for feasibility. Our contribution is a controlled study of touch budget, new-surface adaptation, force/motion accuracy in physical units and the value of tactile information beyond explicit simple baselines. Novelty beyond that requires comparison with the final executed method and results.

## 3. Data and equipment: the first decision

The candidate descriptions below originated in the documentation review. A subsequent bounded HaTT audit established official source access and verified file schemas for three development surfaces, as recorded in the [execution report](execution-report.md). A published collection setup, download link or valid schema does not establish that the released files provide calibrated, aligned channels usable for our protocol.

| Candidate | What the primary documentation describes | Suitable use and unresolved issues |
| --- | --- | --- |
| [Penn Haptic Texture Toolkit (HaTT), author project page](https://heatherculbertson.wixsite.com/home/research), [official manual](https://repository.upenn.edu/bitstreams/960863b6-df14-4770-9068-b1b2bf6a50f1/download) | 100 surfaces, two ten-second freehand recordings each; acceleration, force and position/speed; fixed steel hemispherical tip. | Official access succeeded after the initial web-reading failure. The audit inspected nine XML files for ABS Plastic, Aluminum and Book, preserved the license/manual and verified declared units, counts and finite values. Native rates, calibration, timing, force frame, independent trial relationships and sliding remain unverified. The inspected model archive cannot supply our controlled trial grid or free-motion validation. |
| [HapTex, BUAA](https://haptic.buaa.edu.cn/English_FabricDatabase.htm), [author paper](https://haptic.buaa.edu.cn/dfiles/2019/17.pdf) | 120 fabrics; fingertip friction/normal force, displacement and derived velocity; four strokes per fabric. | Possible force-informed fallback. Human finger contact, limited controlled variation and no separate acceleration channel restrict the claim. Archive contents and redistribution terms remain unverified. |
| [LMT official dictionary](https://zeus.lkn.ei.tum.de/downloads/texture/download/Readme.txt), [release portal](https://zeus.lkn.ei.tum.de/downloads/texture/) | Latest dictionary lists normal/friction force, acceleration and audio; force fields are under FSR friction. | Motion fields are not listed in that dictionary. Force calibration, units, alignment and trial roles need verification. Do not combine older controlled-release procedures with the latest release schema. |
| [Current Cluster recordings](https://github.com/cluster-lab/Cluster-Haptic-Texture-Dataset/blob/main/documents/dataset_details.md), [author paper](https://arxiv.org/html/2407.16206v4) | Acceleration, pressing-force and probe-position recordings; separate friction-property measurements. | The earlier vibration study's data do not supply synchronized per-scan tangential-force targets. Separately measured coefficients with another counterface/condition cannot substitute for those targets. Existing timing uncertainty also remains unresolved. |
| [MIT planar pushing dataset](https://web.mit.edu/mcube/push-dataset/) | Time-stamped pusher/object poses and planar forces, varied conditions and repeated pushes. | Optional separate force/motion benchmark without paired texture-touch sensing. The site states its measurement streams are not synchronized; alignment must be checked. Access, license and loading assumptions need inspection. This would change the experiment's scope. |

**Next route:** resolve the HaTT measurement evidence and independent trial relationships, and identify an existing fixed-probe rig for the controlled experiment and eventual motion stage. The access/schema audit alone does not permit force scoring. If only force-only data are suitable, label that result as force-informed calibration. Revise and freeze an offline protocol before scoring data when the available measurements differ from the proposed design.

The access report should record actual files, native channel rates, units, signs, timestamps, geometry, calibration provenance, independent trial identities, condition coverage and permitted use. Sampling at a common stored rate does not prove a common native bandwidth. Publish download instructions and permissible derived results; verify terms before redistributing raw data.

For a rig, start with two or three development specimens to determine viable force ranges, repeatability and timing. Then choose the calibrated speed/load levels. This is an engineering feasibility check, not the held-out scientific test. Design the pad and mounting so the same contact pairing can be used in the later free-motion stage.

## 4. Measurements and calibration

Required: independent normal and tangential force, actual relative motion, a repeatable tactile/acceleration channel, known geometry and synchronized acquisition. A linear stage is sufficient for prescribed-motion force measurement. Free-response motion is an additional capability.

Before collecting the main pilot:

1. Check force scale, coordinate frame, signs, unloaded zero, drift and cross-axis coupling with known loads across the intended range.
2. Verify motion scale and actual relative sliding. A moving actuator can initially deform a soft pad while the interface sticks. Use contact/sliding evidence appropriate to the fixture.
3. Characterize no-contact guide/cable forces and relevant inertial contributions. Check reference contacts throughout sessions; record wear, debris, cleaning and pad replacement.
4. Verify timestamp scale, offset, drift and acquisition/filter delays. Prefer shared hardware timing where supported; otherwise quantify and correct the alignment using development calibration events.
5. Save immutable raw signals plus separate calibration coefficients, uncertainties, instrument IDs, mounting IDs and derived-data provenance.

ATI distinguishes sensor resolution, repeatability, uncertainty and latency; uncertainty depends on model and calibration and may scale with full range. Choose a range that can resolve the physical differences of interest, then bench-check the selected system. [ATI force/torque FAQ](https://www.ati-ia.com/library/documents/FT_FAQ.pdf).

NI explains that a shared start trigger alone can leave clock drift and that filtering introduces delay. Common software timestamps or interpolated samples need independent validation. [NI synchronization documentation](https://www.ni.com/en/support/documentation/supplemental/10/synchronization-explained.html).

GelSight experiments distinguish elastic deformation, partial slip and full sliding. Motor travel alone should not certify a kinetic-friction interval. [Yuan et al., ICRA 2015](https://people.csail.mit.edu/yuan_wz/GelSight1/ICRA15_2740_FI.pdf).

## 5. Proposed controlled pilot and observation budget

Start with rigid flat specimens, one direction and a fixed pad. The existing plan proposes **8–12 specimens × three speeds × three nominal loads × five independent trials per condition**: 450 trials at ten specimens, plus calibration/reference checks. This is a pilot proposal, not a powered sample size. Determine a later confirmation sample from pilot variability and practical accuracy requirements.

Randomize within workable speed/load/session blocks. Spread roles across sessions when feasible, and avoid always recording queries after calibration. Record specimen/manufacturing groups, session, pad, contact location, trial, condition and calibration IDs. Blocking and randomization help control nuisance variation. [NIST randomized block designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm).

Choose the reference speed/load and valid steady-sliding rule using development data. Initial brief support: the first eligible **0.5 seconds** of one reference-condition trial. This duration is a hypothesis to test. Compare nested durations only if timing, travel and valid windows permit; freeze those budgets beforehand. Report elapsed approach/settling time, total probing time and travel as well as sensor observation time.

Proposed roles for a held-out specimen:

| Role | Permitted use |
| --- | --- |
| Reference-condition trial 0 | Only the declared short prefix is visible to brief methods. |
| Trials 0–2 at all conditions | Larger calibration reference; disclose its extra observations, time and travel. |
| Trials 3–4 at nonreference conditions | Common untouched query trials for all methods. |

Numbers identify trial roles, not chronological order. The main query set excludes the reference speed/load. Define replacements and exclusions from calibration/contact criteria before outcomes are inspected. Log missing cells and compare methods on a common valid domain.

Crop raw support before interpolation, filtering or feature extraction. Fit scalers/features on training specimens only. Support validity and start selection must use permitted observations; preserve independent acquisition/calibration checks as explicitly declared shared infrastructure. Never use query outcomes to choose an especially informative support crop.

## 6. Models and fair input interfaces

For one-dimensional confirmed sliding, begin with:

\[
F_t=-\mu F_n\operatorname{sign}(v),\qquad \mu\geq0.
\]

Here the force is on the moving body and opposes velocity. Transform an instrument's fixture-reaction sign explicitly. Fit the nonnegative coefficient from permitted support forces by least squares; use calibrated minimum load/speed thresholds and inspect systematic sign errors rather than hiding them with clipping.

Compare a global coefficient learned from training specimens, the direct brief per-specimen fit, a modest learned estimator, and the richer calibration reference. Begin with simple features and regularized regression. With a small specimen cohort, a large neural model has little independent training diversity.

Keep two input tracks explicit:

| Track | Brief inference inputs | Essential comparison |
| --- | --- | --- |
| Force-informed | Support normal/tangential forces and declared motion/commands; optionally tactile readings | Force-only fit versus force-plus-tactile at identical support duration and trials. |
| Tactile-informed | Tactile/acceleration and declared commands/conditions; independent support-force labels hidden at inference | Conditions-only estimator versus tactile-plus-conditions at identical support budget. |

Independent force labels can supervise training and score either track. The direct force fit is a useful practical reference for the tactile-informed track, but it has a different measurement interface. Do not attribute its advantage or disadvantage solely to the learning algorithm.

Predeclare a wrong-surface support check for tactile inference, swapping support between specimens at matched conditions. Alongside the conditions-only baseline and rig reference measurements, this tests whether predictions depend on the observed contact rather than only the commands or apparatus signals. A worsening after a swap supports contact-specific information within this setup, not an intrinsic material identification claim.

One touch at one constant speed cannot independently identify both a new specimen's friction level and speed-law slope. A shared slope may be learned from training specimens, or a separately budgeted second-speed touch can be allowed. If comparing that second touch with a repeat, match total observation time and account for extra travel/settling.

Add speed/load dependence only after repeatable residual structure justifies it. Richer static, history, adhesion or compliance models need informative additional measurements. Check parameter ambiguity: similar support fits with divergent later predictions indicate insufficient information. The Burka study motivates testing excitation and budget, without prescribing our duration or model complexity.

## 7. Force evaluation and decision rules

Use complete specimen/material groups for outer holdouts. Choose hyperparameters and preprocessing using only inner training/validation groups. For each outer specimen, permit its brief support and reserve query labels for scoring. Reusing outer results to change methods makes those results development evidence. Model-selection bias is a known risk. [Cawley and Talbot, JMLR 2010](https://www.jmlr.org/papers/v11/cawley10a.html).

A grouped leave-one-specimen-out pilot can assess feasibility. Later confirmation needs frozen rules and new reserved specimens/sessions; a tiny pilot cannot establish universal material generalization. Preserve the [earlier study](https://github.com/EltonChang1/tactile-contact-research/blob/c6fee1245a86bd45c3a6bcbe16c838e1b4a4c5d9/docs/research_plan.md)'s Stage A reserved cohort and data boundary when reusing its data; this mechanical design does not authorize opening those signals.

Proposed primary force metric: tangential-force MAE in newtons, computed within each query trial, averaged over trials per condition, then equally over conditions and held-out groups. Report individual groups, speed/load residuals, paired method differences and uncertainty across independent groups. Sensor timestamps and multiple crops do not increase the number of independent specimens. Intervals from very few groups remain limited evidence.

The principal prediction uses commanded speed and nominal loading for a characterized controlled-load setup. Report actual tracking/loading variability. A separate analysis supplied with future measured query speed or normal force is a **conditional diagnostic**, with those extra inputs declared. For free forward prediction, future measured motion and forces are withheld; load comes from known mechanics or the simulator. Height control alone needs a normal-contact relation or a narrower conditional claim.

Before final scoring, set the practical improvement margin using measurement uncertainty, repeat variability and the later task's tolerance. Declare a primary comparison and whether other comparisons are descriptive. Do not choose a convenient percentage after viewing results, and do not interpret a nonsignificant difference as equivalence. Freeze split/episode manifests, exclusion rules and code/config versions before opening confirmation labels.

## 8. Forward motion, engine integration and task utility

After force feasibility, test a known-mass body with the same pad, geometry and counterface. Begin with horizontal coasting after release, no applied tangential force, and measured initial position/velocity. Account for fixture/cable drag. If weights change loading, record the changed total mass; external loading hardware may introduce other forces.

For the constant-friction idealization, deceleration magnitude is \(a=\mu F_n/m\) and stopping distance is \(v_0^2/(2a)\) when \(a>0\). A gravity-loaded horizontal body has \(F_n=mg\) under the stated assumptions. These formulas are checks of the restricted model, not evidence that real contacts satisfy it.

Compare predicted position/velocity trajectories and stopping distance with independent motion tracking. Keep release measurement, rollout horizon and stopping criteria fixed. Score sliding above a calibrated threshold and specify a stop event that prevents unforced reversal; inspect the near-zero region separately. General sticking, slip onset and reversals require their own model and validation.

A servo-imposed scan tests reaction forces. A real moving body whose trajectory responds to forces tests forward dynamics. Supply initial state, mass, geometry and declared actions; withhold future measured velocity, force and position from rollout inputs.

Start with a one-dimensional model and analytical checks. Then map the validated coefficient into an existing engine such as MuJoCo. Check the effective contact pair: geom priorities/mixing can change the coefficient actually used. Fix solver settings across methods. If a custom tangential law is added, disable corresponding native tangential friction to avoid counting it twice. Save engine/version settings and check timestep sensitivity. [MuJoCo modeling](https://mujoco.readthedocs.io/en/stable/modeling.html#contact-parameters), [contact computation](https://mujoco.readthedocs.io/en/stable/computation/index.html#contact).

If motion improves, use one dragging-to-target task with the same controller and action budget, comparing global versus brief-calibrated parameters. Report target error, success, force-limit violations and adaptation cost. Claims about robot learning or sim-to-real training require a separate matched training and real evaluation. Keep vibration rendering and physical force dynamics as separately testable components.

## 9. What to produce and when to proceed

The table describes physical-study deliverables. Official HaTT access/schema checks and the synthetic force-pilot software exercise are complete; calibration, physical force scoring and the later validation gates remain open. See the [execution report](execution-report.md) for completed work and the [run guide](running-experiment.md) for available commands.

| Gate | Required output | Decision |
| --- | --- | --- |
| Measurement access | File/channel/rights audit or rig capability report, including later free-motion capability | Choose controlled collection, a clearly scoped offline pilot, or a separate mechanics-only benchmark. |
| Engineering feasibility | Calibration, timing, repeatability and operating-range report | Proceed when the measurements can resolve useful physical differences. |
| Force pilot | Versioned trials/episodes, group splits, support budgets, baseline predictions and independent score tables | Determine whether brief adaptation and tactile information merit confirmation; fix the confirmation protocol. |
| Held-out confirmation | Frozen methods, new reserved specimens and paired force results | Proceed with the best supported method, including a simple fit if it wins. |
| Motion validation | Real free-response trajectories and simulation errors | Establish the scope of a useful contact world model. |
| Task validation | Matched controller comparison and adaptation costs | Establish practical value for the chosen task. |

If data access is unavailable, software tests with synthetic data can check signs, units, support boundaries and numerical consistency, but real usefulness remains untested. If force calibration helps while tactile inference does not, report both findings separately. If force errors improve but motion does not, investigate solver assumptions, loading, drag and contact transitions before claiming a world-model benefit.

The immediate deliverable is the remaining measurement audit: calibration, timing, verified sliding, trial independence and rig capability. The existing vibration study can continue independently; an AI victory there is not a prerequisite for this mechanical experiment.

See the [origin note](origin.md) for the source commit and original document hashes.
