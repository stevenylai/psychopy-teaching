# Build Your Own Reaction Time Experiment

In this exercise you will build a simple reaction time experiment **from scratch** in the
PsychoPy Builder. By the end you will have used the three core building blocks of every
PsychoPy experiment:

1. **Routines** – a named sequence of events (like a "scene" in a play)
2. **Components** – the things that happen inside a routine (text on screen, waiting for a key)
3. **Loops** – a way to repeat a routine several times (each pass is called a *trial*)

When you are finished, your experiment should behave like this:

> A welcome screen explains the task. Then, 8 times, a `+` appears, and after a random
> delay a green **GO!** appears. You press the space bar as fast as you can. At the end,
> your average reaction time is shown.

---

## Step 1 – Start a new experiment

1. In the Builder, choose **File → New** (or the New button on the ribbon).
2. You get a blank experiment with one routine called `trial`.
3. Save it early: **File → Save As** and name it `reaction_time.psyexp`.

## Step 2 – Make the welcome routine

1. In the **Routines** panel (top left), right-click the `trial` routine and choose
   **Rename** (or select it and edit its *Name* parameter). Call it `welcome`.
2. In the **Flow** panel (bottom), use **Add Routine** to create two more routines:
   `trial` and `results`.
3. Select the `welcome` routine. In the **Components** panel (top right), click
   **Add Component** and choose **Text**.
4. In the parameter panel, set:
   - *Name*: `instructions`
   - *Text*: your own instructions (copy the ones from the sample if you like)
   - *Duration*: `100` (seconds – effectively "until the participant presses a key")
5. Add a **Keyboard** component:
   - *Name*: `startKey`
   - *Allowed keys*: `space`
   - *Store*: `nothing`
   - *Duration*: `100`
   - *Force end routine*: checked

The routine now waits until the participant presses space.

## Step 3 – Make the trial routine (the heart of the experiment)

Select the `trial` routine and add four components:

| Component | Name | Key settings |
| --- | --- | --- |
| Text | `fixation` | Text: `+`, Duration: `0.5` |
| Text | `stimulus` | Text: `GO!`, Color: green, **Start time**: `1 + random()`, Duration: `10` |
| Keyboard | `response` | Allowed keys: `space`, Store: `last key`, **Start time**: `-1`, Duration: `10`, Force end routine: checked |
| Code | `storeRT` | *End JS Routine*: see below |

The `storeRT` Code component keeps a running list of every reaction time so we can
average them at the end. In its *End JS Routine* box, paste:

```javascript
let rts = psychoJS.experiment.allRTs || [];
let meanRT = rts.length ? Math.round(rts.reduce((a, b) => a + b, 0) / rts.length) : 0;
resultsText.setText('Your average reaction time was ' + meanRT + ' ms');
```

In plain words: make sure a list called `allRTs` exists, then add this trial's reaction
time (`response.rt`) to it.

Two settings are worth understanding:

- **`1 + random()`** – the stimulus appears after a *random* delay of 1–2 seconds,
  so the participant cannot just press the key on a fixed rhythm. (`random()` returns a
  number between 0 and 1, so `1 + random()` is a number between 1 and 2.)
- **Start time `-1`** – the keyboard starts listening *when the previous component
  (the stimulus) starts*, not when the routine starts. This is how PsychoPy measures
  the time between the stimulus and the key press: the reaction time.

## Step 4 – Repeat the trial 8 times with a loop

1. In the **Flow** panel, click **Add Loop** and choose **TrialHandler**.
2. Name it `trials` and set *N reps* to `8`.
3. Drag the `trial` routine **inside** the loop (between the loop's start and end).

Your flow should now read:

```text
welcome → [ trials: 8 × trial ] → results
```

This is the most important idea in this course: **a loop runs the routine inside it once per trial, and PsychoPy automatically saves one row of data per trial** (including `response_rt`, the reaction time).

## Step 5 – Show the results

> **Note:** the experiment runs in the browser (PsychoJS), so any Code component must use **JavaScript**, in the *Begin JS Routine* box – **not** the Python *Begin Routine* box. (The Python box is ignored when exporting to the browser.) You can copy the code below; you don't need to write it from scratch.

Select the `results` routine and add:

1. A **Code** component named `calcResults`. In its *Begin JS Routine* box, paste:

   ```javascript
   let rts = psychoJS.experiment.allRTs || [];
   let meanRT = rts.length ? Math.round(rts.reduce((a, b) => a + b, 0) / rts.length) : 0;
   resultsText.setText('Your average reaction time was ' + meanRT + ' ms');
   ```

   In plain words: take the list of reaction times that `storeRT` collected, average them, round to a whole number of milliseconds, and put that number into the `resultsText` component.

2. A **Text** component named `resultsText` with:
   - *Text*: `Calculating your results...` (the code above replaces this with the real number)
   - *Duration*: `100`
3. A **Keyboard** component named `endKey` (space, store `nothing`, duration `100`, force end routine) so the participant can close the experiment.

## Step 6 – Check your work

- [ ] The flow shows `welcome`, the `trials` loop containing `trial`, then `results`
- [ ] The stimulus starts at `1 + random()`
- [ ] The response keyboard starts at `-1` and stores `last key`
- [ ] The `storeRT` Code component adds `response.rt` to `allRTs`
- [ ] The loop runs 8 trials
- [ ] The results text shows a number in milliseconds

Compare with the finished version: open `/examples/reaction_time.psyexp` in a new Builder window and look at each routine.

## Challenge (optional)

Turn it into a **Go/No-Go** task:

1. Create a CSV file with two rows: one where the stimulus is `GO!` (green) and one where it is `NO!` (red).
2. Point the loop's *Conditions file* parameter at your CSV.
3. In the `NO!` row, the correct answer is to **not** press the key.
4. Set the keyboard's *Correct answer* and *Store correct* so PsychoPy scores each trial.

Now your experiment has *conditions* – the next big idea after loops.
