"""HTML block with the equations behind every number in the nested-loss reports (E68, E71a).
Each equation is taken from the code that ran: src/isj/worlds.py, src/isj/encoder.py (train_encoder), src/isj/stage_b1.py
(slice_measures, invariance_residual), src/isj/audits.py (mlp_r2, r2), src/isj/engine.py (fit_whitener, difference_moment)."""

CSS = """
.eq{background:#f8fafc;border-left:4px solid #6366f1;padding:7px 14px;margin:6px 0;font:16px/1.7 'Cambria Math',Cambria,'STIX Two Math','Times New Roman',serif;overflow-x:auto}
.eqn h3{font-size:15.5px;margin:16px 0 2px}.eqn p{margin:3px 0;font-size:14px;color:#334155}.eqn .w{color:#475569;font-size:13.5px}
"""

def E(s): return f'<div class="eq">{s}</div>'

def equations_html():
    return f"""<h2>8. The equations behind the numbers</h2>
<div class="eqn">
<p class="w">Notation: K layers of 4 numbers each, so d = 4K numbers; z = [z<sub>1</sub> | ... | z<sub>K</sub>] are the hidden numbers (z<sub>b</sub> has 4), z<sub>1</sub> the fastest. Every formula below is the one the code ran.</p>

<h3>A. From nothing to the input data</h3>
<p><b>1. Hidden numbers over time</b> (one chain per block b, the same speed ρ<sub>b</sub> for its 4 numbers, unit variance at every step):</p>
{E("z<sub>t+1,b</sub> = ρ<sub>b</sub> · z<sub>t,b</sub> + √(1 − ρ<sub>b</sub><sup>2</sup>) · ε<sub>t,b</sub>,&nbsp;&nbsp; ε ~ N(0, I<sub>4</sub>),&nbsp;&nbsp; z<sub>t,b</sub> ~ N(0, I<sub>4</sub>)")}
<p>Speeds: E68 uses ρ = 0.2, 0.5, 0.75, 0.95. E71a uses 1 − ρ<sub>b</sub> = 0.8 · 0.05<sup>(b−1)/(K−1)</sup>, i.e. ρ<sub>b</sub> runs from 0.2 to 0.96.</p>
<p><b>2. What the encoder sees</b> (the observation map, not trained): four alternating layers, then the observed numbers x ∈ R<sup>d</sup> (as many as hidden numbers; no extra dimensions):</p>
{E("odd layers:&nbsp; z<sub>R</sub> := z<sub>R</sub> + tanh(z<sub>L</sub> W<sub>i</sub>);&nbsp;&nbsp; even layers:&nbsp; z<sub>L</sub> := z<sub>L</sub> + tanh(z<sub>R</sub> W<sub>i</sub>);&nbsp;&nbsp; W<sub>i</sub> = s · Q<sub>i</sub>")}
<p>z<sub>L</sub>, z<sub>R</sub> are the first and second half of the d numbers, Q<sub>i</sub> is a fixed random orthogonal matrix, s is the coupling strength (0.5 in E71a; 1, 2, 4, 8 in E68). Larger s bends the space more.</p>
<p><b>3. Matched pairs for rung k</b> (u, v): they share every layer slower than k and redraw layers 1 to k:</p>
{E("u ~ N(0, I<sub>d</sub>);&nbsp;&nbsp; v<sub>b</sub> = u<sub>b</sub> for b &gt; k;&nbsp;&nbsp; v<sub>b</sub> ~ N(0, I<sub>4</sub>) fresh for b ≤ k")}

<h3>B. The encoder and the loss</h3>
<p><b>4. Encoder and predictor</b> (both small MLPs, GELU): h = g(x) = W<sub>3</sub>·GELU(W<sub>2</sub>·GELU(W<sub>1</sub>x)), widths d → 16K → 16K → d. The output is cut into fixed slices h = [h<sub>1</sub> | ... | h<sub>K</sub>], 4 numbers each; slice b is meant to hold layer b. The predictor f has the same shape.</p>
<p><b>5. Training loss</b> for one step: N = 256 transitions (z<sub>t</sub>, z<sub>t+1</sub>), h<sub>t</sub> = g(C(z<sub>t</sub>)), h<sub>t+1</sub> = g(C(z<sub>t+1</sub>)), and for each k = 1, ..., K−1 a batch of 256 rung-k pairs with outputs h<sup>u</sup>, h<sup>v</sup>:</p>
{E("L = L<sub>pred</sub> + Σ<sub>k=1</sub><sup>K−1</sup> [ 1 · L<sub>inv,k</sub> + W · L<sub>wd,k</sub> ] + W · L<sub>wh</sub> + 0.01 · L<sub>var</sub> + 0.04 · L<sub>cov</sub>")}
{E("L<sub>pred</sub> = (1 / N d) Σ ‖ f(h<sub>t</sub>) − sg(h<sub>t+1</sub>) ‖<sup>2</sup>&nbsp;&nbsp;&nbsp; (<b>predictive loss</b>: mean squared error over the batch and all d coordinates; sg = stop-gradient on the target)")}
{E("L<sub>inv,k</sub> = mean over pairs and over the tail coordinates of ( h<sup>u</sup><sub>T</sub> − h<sup>v</sup><sub>T</sub> )<sup>2</sup>,&nbsp;&nbsp; T<sub>k</sub> = slices k+1, ..., K&nbsp;&nbsp;&nbsp; (the slower slices must agree across a rung-k pair)")}
{E("L<sub>wd,k</sub> = ‖ Cov( h<sup>u</sup><sub>k</sub> − h<sup>v</sup><sub>k</sub> ) − 2 I<sub>4</sub> ‖<sub>F</sub><sup>2</sup>&nbsp;&nbsp;&nbsp; (slice k must still vary across the pair: two independent unit-variance draws differ with covariance 2I)")}
{E("L<sub>wh</sub> = ‖ Cov(h) − I<sub>d</sub> ‖<sub>F</sub><sup>2</sup>&nbsp;&nbsp;&nbsp; (all outputs spread out, uncorrelated, unit variance)")}
{E("L<sub>var</sub> = Σ<sub>j</sub> max(0, 1 − √(Var(h<sub>j</sub>) + 10<sup>−4</sup>)),&nbsp;&nbsp;&nbsp; L<sub>cov</sub> = (1/d) Σ<sub>i≠j</sub> Cov(h)<sub>ij</sub><sup>2</sup>")}
<p>Cov and Var are over the 512 encoded points of the batch (z<sub>t</sub> and z<sub>t+1</sub> together). The weights 1, 0.01 and 0.04 are fixed; W is 1 or 10, picked per world by a 10,000-step pilot (the smaller one whose smallest eigenvalue of Cov(h) stays at least 0.5); it was 1 in every world. Optimizer AdamW, learning rate 3·10<sup>−3</sup> for the first half of the steps, then cosine decay to 0; 7,500 K steps (E71a) or 30,000 (E68). <b>Arm A</b> has every k-term on from step 0; <b>arm B</b> switches the k-term on at step 5,000 (k − 1).</p>
<p><b>6. Reference for the predictive loss.</b> If every layer is kept and each output coordinate has unit variance, the best one-step prediction of a coordinate of block b leaves variance 1 − ρ<sub>b</sub><sup>2</sup> (from equation 1), so</p>
{E("L<sub>pred</sub><sup>ref</sup> = (1/K) Σ<sub>b</sub> ( 1 − ρ<sub>b</sub><sup>2</sup> )&nbsp;&nbsp;&nbsp; (0.561 for the E68 speeds; 0.412, 0.410, 0.408 for K = 11, 13, 16)")}
<p>The reported predictive loss is L<sub>pred</sub> at the last training step (one batch of 256 transitions), averaged over the 5 seeds; the reference assumes whitened outputs, so it is an approximate floor, not an exact one.</p>

<h3>C. How the results are read out (fresh data; the trained encoder is frozen)</h3>
<p>20,000 fresh hidden vectors z are drawn, passed through C and g to get raw outputs h (no whitening); the first 15,000 are used to fit the readouts, the last 5,000 to score them.</p>
<p><b>7. Presence and leakage.</b> For a slice a and a layer c, fit a small network (tanh, 64 hidden units, 800 Adam steps, batches of 1,024; inputs and targets standardized) from h<sub>a</sub> to z<sub>c</sub> on the 15,000, then on the 5,000:</p>
{E("R<sup>2</sup>(z<sub>c</sub> from h<sub>a</sub>) = 1 − Σ ( z<sub>c</sub> − ẑ<sub>c</sub> )<sup>2</sup> / Σ ( z<sub>c</sub> − mean(z<sub>c</sub>) )<sup>2</sup>&nbsp;&nbsp; (sums over test points and the 4 numbers of the layer)")}
{E("presence<sub>b</sub> = R<sup>2</sup>(z<sub>b</sub> from h<sub>b</sub>);&nbsp;&nbsp;&nbsp; leakage<sub>b</sub> = max<sub>c &lt; b</sub> R<sup>2</sup>(z<sub>c</sub> from h<sub>b</sub>)&nbsp;&nbsp; (b ≥ 2)")}
<p>Presence 1 means layer b can be read perfectly from its own slice; 0 means not at all. Leakage is how well any faster layer can be read from the slice.</p>
<p><b>8. Invariance residual</b> for rung k, on 5,000 fresh rung-k pairs, T = slices k+1 to K:</p>
{E("r<sub>k</sub> = mean( h<sup>u</sup><sub>T</sub> − h<sup>v</sup><sub>T</sub> )<sup>2</sup> / mean<sub>j∈T</sub> Var( h<sup>u</sup><sub>j</sub> )")}
<p>0 = the slower slices are identical across the pair. For two unrelated points the numerator is 2 × the variance, so r = 2.</p>
<p><b>9. Health</b> = λ<sub>min</sub>( Cov(h) ), the smallest eigenvalue of the output covariance on the 20,000 points: near 0 means an output direction is dead.</p>
<p><b>10. Clean rung and clean seed.</b> Rung k (1 ≤ k &lt; K) is clean if presence<sub>k</sub> ≥ 0.9, leakage<sub>k</sub> ≤ 0.1 (k ≥ 2) and r<sub>k</sub> ≤ 0.05. A seed is all-rungs-clean if every rung is clean and health ≥ 0.5; slice K (the core) is read only for presence. In E68 a seed is slice-clean if all presence<sub>b</sub> ≥ 0.9, all leakage ≤ 0.1 and health ≥ 0.5. The clean-rung fraction at K = 16 is the mean over seeds of (clean rungs)/15.</p>
<p><b>11. The pair-difference spectrum</b> (best-seed page). With 30,000 fresh points, the outputs are whitened (ZCA): r = C<sup>−1/2</sup>(h − mean(h)), C = Cov(h). With 30,000 rung-k pairs and D = r(u) − r(v), restricted to the directions H<sub>k−1</sub> not yet removed by earlier rungs:</p>
{E("M<sub>k</sub> = H<sub>k−1</sub><sup>T</sup> [ (1/n) Σ D D<sup>T</sup> ] H<sub>k−1</sub>;&nbsp;&nbsp; eigenvalues λ<sub>1</sub> ≥ λ<sub>2</sub> ≥ ...")}
<p>A direction the pair changes in has eigenvalue about 2 (unit-variance, independent redraw); a direction it leaves alone has eigenvalue near 0. Rung k changes layers 1 to k, so a clean nested split gives 4k large eigenvalues. The "ratio" column is the last large eigenvalue divided by the first small one.</p>
<p><b>12. Global R<sup>2</sup></b> (best-seed page): a linear ridge fit from the 4K hidden numbers z to the whitened output r on the 15,000, scored on the 5,000: R<sup>2</sup> = 1 − Σ(r − r̂)<sup>2</sup> / Σ(r − mean r)<sup>2</sup>. It says how much of the embedding is a linear function of the hidden numbers.</p>
<p><b>13. Rank correlation</b> between the predictive-loss excess and the mean presence over the 55 runs: the Pearson correlation of the ranks (Spearman), excess = L<sub>pred</sub> − L<sub>pred</sub><sup>ref</sup>, mean presence = (1/K) Σ<sub>b</sub> presence<sub>b</sub>.</p>
</div>"""
