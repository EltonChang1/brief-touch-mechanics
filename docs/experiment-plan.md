# Experiment plan: a brief touch that improves a robot's contact model

**Drafted: 10 October 2026; status updated: 12 October 2026. The force-pilot software and HaTT access/schema audit are implemented. The physical protocol remains provisional, with no real force-prediction, motion or robot-task results yet.**

This is the execution plan for the experiment described in the [README](../README.md). The [methods review](methods.md) supplies calibration details, dataset candidates and research context. Numbers below are proposed engineering targets, not achieved results or thresholds established by the literature. Finalize them using development/pilot measurements, then freeze them before confirmation.

## 1. Clear goal and scope

**Primary goal:** after observing 0.5 seconds of verified sliding on a previously unseen surface, predict tangential forces in independent later slides at other speeds and loads more accurately than a simulator using one global friction coefficient.

**Next goal:** use the same contact estimate to predict a freely moving body's trajectory and stopping distance, then use it to improve a robot slide-to-target task.

The scientific questions are separate:

| Question | Decisive comparison | Evidence needed |
| --- | --- | --- |
| Does a brief touch enable useful adaptation? | Brief force fit versus global friction | Lower force error on whole held-out surface groups |
| Does tactile/texture sensing add information? | Tactile model versus its matched estimator without tactile inputs | Improvement with identical support duration and otherwise identical inputs |
| Does this help a physical world model? | Adapted versus global model in independent free-motion rollouts | Lower trajectory and stopping errors without future measurements |
| Does this help a robot act? | Same controller using adapted versus global contact parameters | Lower target error under the same action limits |

Start with flat, rigid specimens, one sliding direction, one fixed pad and a bounded speed/load range. The estimate describes that pad-surface pairing. Friction depends on the interacting system and conditions; changing a gripper, foot or object's underside requires another transfer experiment. [NIST SP 960-11, section 6.3.2.6](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication960-11.pdf).

## 2. Baseline and proposed method

Begin with Coulomb sliding friction:

\[
F_t=-\mu F_n\operatorname{sign}(v),\qquad \mu\geq 0.
\]

The sign describes the force on the moving body. Convert fixture-reaction measurements into this convention explicitly.

| Method | New-surface observation | Purpose |
| --- | --- | --- |
| **B0: global friction** | None | Fit one nonnegative coefficient across training groups, weighting groups equally. This is the primary baseline. |
| **B1: direct brief force fit** | Normal/tangential forces and motion from the allowed 0.5-second support | Estimate a new coefficient by nonnegative least squares. This is the primary adaptation method and a strong simple reference. |
| **B2: conditions-only estimator** | Declared support speed/load/commands; no tactile or force signal | Test how much a learned model can infer without observing the new contact. |
| **T1: tactile estimator** | Tactile/acceleration features plus B2's conditions | Compare against B2 to test tactile information when independent support forces are unavailable at inference. |
| **B3 / T2: matched force estimators** | Support-force features and conditions, without/with tactile features | Use the same regression family and tuning procedure. Compare T2 against both B3 and B1 to test added tactile value when forces are available. |
| **R: extended calibration** | Three support trials at each of nine conditions | Estimate the achievable accuracy with more observations; disclose its extra time/travel. This is an empirical reference, not an oracle. |

Independent force measurements supervise training and score every method. Hide them from T1 at new-surface inference. B1 and T1 have different sensing interfaces, so their comparison alone cannot establish tactile's added value.

Use a small fixed feature set and regularized regression first: vibration RMS, fixed spectral-band powers and force summaries where permitted. Fit transformations and hyperparameters using training groups only. A large neural model is a later option if independent surface diversity warrants it.

A single touch at one constant speed identifies an effective coefficient, not independent friction, speed dependence, stiffness and adhesion parameters. Add a shared speed law or separately budgeted second-speed touch only if pilot residuals justify it; freeze that extension before confirmation.

## 3. Equipment and measurement gate

Use an existing motorized linear slide, a fixed pad, independent normal/tangential force sensing, a mounted acceleration or tactile sensor, and actual motion measurement. Design the fixture so the same pad and contact geometry can later be attached to a known-mass freely sliding body. A position-controlled slide provides force measurements; it cannot establish free-motion prediction.

Before the main pilot, use **2-3 development specimens**, excluded from pilot and confirmation, to produce:

1. A channel/rig audit: native sampling rates, units, signs, timestamps, sensor and pad IDs, calibration provenance, travel and force limits, and free-motion capability.
2. Force scale/zero/cross-axis checks, guide/cable/inertial-force characterization and a session reference contact.
3. Timing and filter-delay verification using shared events; measure residual offset and drift. Interpolation does not prove synchronization.
4. Evidence that selected windows contain actual interface sliding, rather than deformation of a sticking pad.
5. A repeatability and wear report, including cleaning/preparation rules and a pad replacement rule.

Draft force conditions are **50, 150 and 300 mm/s**, at **1, 2 and 4 N**, with the middle speed/load as the reference. These are starting values to check against rig capability, not assumed available settings. A 0.5-second reference observation covers 75 mm; the fastest window covers 150 mm, before approach, acceleration and settling. Verify the available travel.

Draft measurement objectives are force uncertainty no greater than **0.01 N**, residual timing error no greater than **2 ms**, and later position uncertainty no greater than **0.25 mm**. Verify the relevant bandwidth and filtering as well as these values. If these objectives or conditions are unsuitable, revise the tolerances and protocol on development data before collecting the main pilot.

**Gate:** proceed only when valid sliding windows and repeatability can resolve the improvement being tested. A bounded Penn Haptic Texture Toolkit audit has established official source access and verified schemas for three development surfaces; see the [execution report](execution-report.md). Calibration, native rates, timing, force frame, independent trial relationships and sliding remain unverified, and rig access is unconfirmed. Its uncontrolled recordings do not replace controlled trials or free-motion validation; revise and freeze an offline protocol before scoring.

## 4. Controlled force pilot

Collect **10 independent surface groups × 3 speeds × 3 loads × 5 independent trials = 450 trials**, plus development/calibration checks. Choose a range of rigid surfaces and finishes within the intended deployment domain. Multiple coupons from the same sheet or manufacturing batch remain in one group; they do not increase the independent group count.

Each valid trial supplies a predefined 0.5-second steady-sliding window. Assign roles before acquisition:

| Role on each held-out surface | What the methods may see |
| --- | --- |
| Reference-condition trial 0 | Brief methods see only the first eligible 0.5 seconds. |
| Trials 0-2 at all nine conditions | R sees 27 windows, totaling 13.5 seconds of valid sliding, versus B1/T1/T2's 0.5 seconds. |
| Trials 3-4 at the eight nonreference conditions | All methods predict these **16 common untouched query trials**. |
| Reference-condition trials 3-4 | Reserved for predefined repeatability reporting; excluded from the primary query score. |

Trial numbers denote roles, not collection order. Randomize roles within workable speed/load/session blocks, spread repetitions across sessions where feasible, and log location, specimen, pad, session, calibration and trial IDs. Report full probing time and travel, including approach and settling; 0.5 seconds is the sensor observation budget.

Evaluate nested **0.1, 0.25 and 0.5-second** support prefixes as secondary pilot analyses, with a common start. Crop support before filtering/interpolation/features and handle boundaries without reading the forbidden remainder. Support start and exclusions use permitted observations and predefined measurement rules, never future query errors.

Hold out entire surface groups in outer pilot evaluation. Select models and preprocessing inside the remaining training groups. The pilot can guide development; it is not final confirmation. Keep any reserved data from the earlier vibration project closed.

Primary queries use commanded speed and nominal normal load from a characterized controlled-load setup. Report tracking/load variation. A separate score using actual future query speed/load is a conditional diagnostic and must be labeled with those extra inputs.

## 5. Metrics, success targets and confirmation

Compute tangential-force MAE in newtons for each query trial, average repetitions within each condition, then conditions within each group, then weight groups equally. Show errors by group, speed and load, rather than reporting only a pooled sample score.

For each comparison, report paired group differences, a 95% uncertainty interval resampling whole independent groups, and absolute as well as percentage improvement. Samples, windows and repeated trials are not independent surface groups. Inspect uncertainty in calibrated measurements and trial repeatability separately from between-group uncertainty.

| Endpoint | Proposed practical target |
| --- | --- |
| Primary brief adaptation: B1 versus B0 | At least **25% lower** group-balanced force MAE, at least **0.02 N** absolute reduction, and B1 MAE at most **0.10 N** |
| Added tactile information: T1 versus B2; T2 versus B3 and B1 | At least **15% lower** MAE against the relevant references, with absolute reduction above the frozen measurement/repeatability floor |
| Forward motion: B1 versus B0 | At least **25% lower** stopping-error score, including the declared failure penalty, and adapted score at most **2 mm** |
| Robot task: adapted versus global | At least **20% lower** target-error score, including the declared failure penalty, with at least **80%** of adapted trials finishing within **2 mm** |

These are proposed engineering targets. Check their relevance and feasibility using pilot variability and intended task tolerances. Freeze any revisions before confirmation. For a supported improvement claim, require the practical point-estimate target and a paired 95% interval supporting improvement. A wide interval means inconclusive evidence; a nonsignificant difference does not demonstrate equivalence.

Make **B1 versus B0 force error the single primary confirmation comparison**. Treat tactile, motion and task findings as gated secondary evidence and report all prespecified comparisons. Do not search the final results for a winning input track, metric or method.

Budget initially for **12 new independent confirmation groups × 45 trials = 540 trials**. Determine the final group count from pilot paired variability: target 80% power for the frozen practical force difference at a two-sided 5% level, and check expected interval precision. Increase the cohort before confirmation if needed; 12 is a planning allowance, not a powered sample-size claim. If the required cohort is unaffordable, report an exploratory confirmation with its uncertainty.

Before opening confirmation query labels, freeze the manifest, sample size, support interface/budget, feature set, models, primary comparison, thresholds, exclusions/replacements, uncertainty procedure, motion/task protocols and code/config versions. Train on development/pilot groups only. Each new group contributes its allowed support, never query labels for tuning. Freeze predictions before scoring.

## 6. Validate movement, then robot action

### Free-motion experiment

Use the same pad/contact geometry under a horizontal body with known total mass and measured release state. Characterize residual guide/air/cable forces. For an ideal gravity-loaded Coulomb contact:

\[
a=\mu g,\qquad d_{\mathrm{stop}}=\frac{v_0^2}{2\mu g}.
\]

Use these analytical predictions before integrating a general engine. Choose total body mass so its gravity load lies within the validated force range. Preserve the pad geometry and tactile-sensor mounting; validate any mounting change on development data before confirmation. For a non-gravity-loaded fixture, use its actual known loading and mass instead. Record changes in total mass when adding weights.

On the confirmation surfaces, collect **three release speeds × five repetitions per group**: 180 trajectories if there are 12 groups. Select speeds during development within the validated force range, with stopping distances large enough for the tracker and task tolerance to be meaningful. If the range cannot support this, broaden and validate the force protocol before confirmation. Fix the release procedure, rollout horizon, low-speed threshold and stop event, preventing unforced numerical reversal.

Coasting necessarily passes through speeds below the smallest controlled force condition. Report that near-zero segment separately; the movement experiment also tests this extrapolation and the stop transition. Do not infer general sticking or slip-onset accuracy from a kinetic-friction fit.

Use one fresh declared 0.5-second support per surface for this phase, without refreshing it per trajectory; R receives 27 separate 0.5-second windows across the nine force conditions. Keep release trials independent and forbid parameter updates from them. Evaluate B0, B1 and R on the same real trajectories, with any tactile model fixed in advance from the pilot. Provide initial position/velocity, mass, geometry and declared actions. Withhold future measured force, velocity and position from prediction. Report stopping-distance MAE in mm, trajectory position RMSE, velocity error and stop-time error.

Freeze the maximum tracking time and usable travel distance **L** on development data. For the primary stopping-error score, use absolute stopping-distance error when both stops are observed/predicted within those limits; otherwise assign the fixed failure penalty **L**. Report failure/censoring counts and completed-trial MAE separately. A zero friction estimate predicts no finite stop for a moving body; retain it under this rule rather than introducing a coefficient floor after confirmation. Do not drop trajectories that fail to stop or leave the tracking region.

Once the simple dynamics agree with the real body, integrate the coefficient into **one existing physics engine**, initially MuJoCo. Use an explicit contact pair or inspect effective contact coefficients; mixing rules can otherwise change the applied value. Keep solver settings identical and check timestep sensitivity. Avoid adding custom tangential friction on top of native tangential friction. [MuJoCo contact parameters](https://mujoco.readthedocs.io/en/stable/modeling.html#contact-parameters).

### Robot slide-to-target experiment

Have the robot launch/release the same gravity-loaded body toward three target distances within the validated motion range. Use the same controller, action/force limits, release mechanism and state feedback for both methods; change only global versus brief-calibrated contact parameters. For the simple model, the planned release speed is \(v_0=\sqrt{2\hat\mu g d_{\mathrm{target}}}\). The release mechanism's tracking error must be measured on development data. Freeze common target distances and speed limits using development data; clip all methods' requested speeds to those limits and report saturation. Do not tailor targets or exclude failures using confirmation outcomes.

Collect **three targets × five repetitions × two methods per group**: 360 trials at 12 groups. Randomize method/target order. B1 receives one fresh 0.5-second support per surface for this phase, separate from task trials and shared across its target repetitions; B0 receives no support. Do not update parameters from task outcomes. Include probe and computation time in adaptation cost. A continuously position-servoed drag can mask friction errors, so the decisive outcome is the body's free stop after release.

Report target error, success within the frozen 2 mm tolerance, force/action-limit violations and total adaptation time. A successful force fit can remain the preferred method if tactile learning adds no benefit.

Apply the same fixed **L** penalty to task trials without an observed stop within the time/travel limits; report ordinary completed-trial target MAE as well. Retain saturated commands, zero-launch predictions and other action failures. A zero launch that leaves the body stationary has its ordinary target error and success/failure outcome.

## 7. Why this matters for tactile/texture world models

The proposed architecture is:

**Brief contact observation → contact estimate and uncertainty → predicted forces → action-conditioned motion → robot action.**

A physics engine supplies the dynamics; this experiment supplies a way to adapt its contact parameters from an observation. A learned world model could instead condition future-state prediction on the inferred contact representation. The central capability is predicting what an action will do on a new contact.

Texture sensing describes part of the interaction through vibrations, deformation or tactile images. It may carry useful information about friction and changing contact conditions, but that relationship must be measured. Accurate vibration generation or texture classification alone does not validate mechanical forces or movement.

| Result achieved | Meaning for the larger project |
| --- | --- |
| Force adaptation succeeds | A small contact model can calibrate rapidly on new surfaces. |
| Tactile comparisons also succeed | Texture/tactile observations add useful mechanical information under the tested sensing interface. |
| Independent movement prediction succeeds | The calibrated contact module is a validated component of a restricted physical world model. |
| The robot task also succeeds | Adapting the model has practical value for this manipulation task. |

Related research supports this direction: [DiffTactile](https://arxiv.org/html/2403.08716v1) identifies simulator parameters using real force and tactile-marker observations; [RoboPack](https://www.roboticsproceedings.org/rss20/p130.html) uses tactile-informed dynamics for real pushing and packing. [Visuo-Tactile World Models](https://arxiv.org/html/2602.06001v1) reports contact-aware prediction/planning, while its limitations leave broader physical generalization open. These systems use different interfaces and observation histories; none establishes our half-second budget or result.

Our proposed contribution is controlled evidence about **how little contact observation is useful, whether tactile information adds value beyond simple calibration, and whether that gain survives into real motion and action on held-out surfaces**. It is a foundation for a larger engine/world model, not a claim that the full system has been built.

After these gates, expand one factor at a time: speed/load laws, slip onset and sticking, direction-dependent friction, compliant contact, changed counterfaces, coupled tactile-signal rendering, and finally multi-contact robot tasks. Validate each extension independently. Benefits for sim-to-real policy training require a later matched training and robot evaluation.

## 8. Work schedule and concrete deliverables

Assume an accessible rig and one researcher with mechanical/data support. Hardware procurement or major fixture construction extends the schedule; the week count starts when equipment is available.

| When | Work | Reviewable deliverable / gate |
| --- | --- | --- |
| Weeks 1-2 | Audit equipment/data; calibrate with 2-3 development specimens | Access report, rig schematic, calibration/timing/repeatability report and final pilot ranges |
| Weeks 3-4 | Collect 450 pilot force trials; implement simple estimates and matched tactile comparisons | Trial/episode manifests, grouped pilot predictions, force errors and support-budget curves |
| Week 5 | Choose confirmation cohort and freeze protocol | Sample-size justification, immutable protocol/config/model versions and predefined motion/task procedures |
| Weeks 6-7 | Collect confirmation force trials and score frozen predictions | Paired B1/B0 force results, tactile comparisons and an explicit proceed/revise decision |
| Weeks 8-9 | Collect independent free-motion trajectories; verify analytical model and engine | Trajectory/stopping errors, engine contact settings and timestep check |
| Week 10 | Run matched robot target task if motion passes | Target errors, success, action limits and adaptation cost |

Implemented software includes immutable CSV ingestion with explicit calibration/unit/sign conversion; trial and support/query manifests; B0/B1 and matched regression estimators; grouped force-pilot evaluation; and analytical one-dimensional stop-aware rollout. These have run on synthetic contacts and passed software checks; the calibration converter still requires measured bench coefficients. Available commands and data contracts are in the [run guide](running-experiment.md). Remaining work includes real measurement validation, support-budget analyses, frozen confirmation, engine integration and the robot task runner.

If brief force calibration fails, inspect measurement quality, support budget and speed/load dependence before expansion. If force calibration works but tactile inference does not, retain and report the simple calibration result. If force predictions improve but movement does not, examine loading, parasitic forces and contact transitions. Each outcome resolves a useful question without overstating the stage reached.

**Immediate next action:** complete the calibration, timing, sliding and trial-independence evidence for an appropriate paired-channel dataset or confirm and characterize a force/tactile rig. Pass the physical measurement gate before scoring real force predictions.
