import { createSlice, PayloadAction } from "@reduxjs/toolkit"

type AdvancedModeState = { value: boolean }
const initialState: AdvancedModeState = { value: false }

const advancedModeSlice = createSlice({
    name: 'advancedMode',
    initialState,
    reducers: {
        set: (s, a: PayloadAction<boolean>) => {
            s.value = a.payload;
        },
    },
});

export const { set } = advancedModeSlice.actions;
export default advancedModeSlice.reducer;