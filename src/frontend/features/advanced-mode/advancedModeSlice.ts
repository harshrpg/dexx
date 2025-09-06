import { AdvancedModeState } from "@/types/chatInput";
import { createSlice, PayloadAction } from "@reduxjs/toolkit"

const initialState: AdvancedModeState = { value: false, symbol: 'BTC/USD' }

const advancedModeSlice = createSlice({
    name: 'advancedMode',
    initialState,
    reducers: {
        set: (s, a: PayloadAction<AdvancedModeState>) => {
            s.value = a.payload.value;
            s.symbol = a.payload.symbol;
        },
    },
});

export const { set } = advancedModeSlice.actions;
export default advancedModeSlice.reducer;