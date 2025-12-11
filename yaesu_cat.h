#ifndef YAESU_CAT_H
#define YAESU_CAT_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif


// Enumerate all CAT commands
typedef enum {
    CATCMD_AB, CATCMD_AC, CATCMD_AG, CATCMD_AI, CATCMD_AM, CATCMD_AN, CATCMD_AO, CATCMD_AV,
    CATCMD_BA, CATCMD_BC, CATCMD_BD, CATCMD_BI, CATCMD_BM, CATCMD_BP, CATCMD_BS, CATCMD_BU, CATCMD_BY,
    CATCMD_CH, CATCMD_CN, CATCMD_CO, CATCMD_CS, CATCMD_CT,
    CATCMD_DA, CATCMD_DN, CATCMD_DT,
    CATCMD_ED, CATCMD_EM, CATCMD_EN, CATCMD_EU, CATCMD_EX,
    CATCMD_FA, CATCMD_FB, CATCMD_FN, CATCMD_FR, CATCMD_FS, CATCMD_FT, CATCMD_GT,
    CATCMD_ID, CATCMD_IF, CATCMD_IS,
    CATCMD_KM, CATCMD_KP, CATCMD_KR, CATCMD_KS, CATCMD_KY,
    CATCMD_LK, CATCMD_LM,
    CATCMD_MA, CATCMD_MB, CATCMD_MC, CATCMD_MD, CATCMD_MG, CATCMD_ML, CATCMD_MR, CATCMD_MS, CATCMD_MT, CATCMD_MW, CATCMD_MX,
    CATCMD_NA, CATCMD_NB, CATCMD_NL, CATCMD_NR,
    CATCMD_OI, CATCMD_OS, CATCMD_PA, CATCMD_PB, CATCMD_PC, CATCMD_PL, CATCMD_PR, CATCMD_PS,
    CATCMD_QI, CATCMD_QR, CATCMD_QS,
    CATCMD_RA, CATCMD_RC, CATCMD_RD, CATCMD_RF, CATCMD_RG, CATCMD_RI, CATCMD_RL, CATCMD_RM, CATCMD_RS, CATCMD_RT, CATCMD_RU,
    CATCMD_SC, CATCMD_SD, CATCMD_SF, CATCMD_SH, CATCMD_SM, CATCMD_SQ, CATCMD_SS, CATCMD_ST, CATCMD_SV, CATCMD_SY,
    CATCMD_TX,
    CATCMD_UL, CATCMD_UP, CATCMD_VD, CATCMD_VG, CATCMD_VM, CATCMD_VS, CATCMD_VT, CATCMD_VX,
    CATCMD_XT, CATCMD_ZI,
    CATCMD_UNKNOWN
} CatCommandId;

typedef struct {
    const char* mnemonic;      // e.g., "FA"
    const char* description;   // e.g., "Frequency Main Band"
    uint8_t paramCount;        // Number of parameter bytes (not including mnemonic or ';')
    CatCommandId id;           // Enum for switch/case
} CatCommand;
const CatCommand catCommands[] = {
    { "AB", "Main band to sub band", 0, CATCMD_AB },
    { "AC", "Antenna tuner control", 0, CATCMD_AC },
    { "AG", "AF gain", 0, CATCMD_AG },
    { "AI", "Auto information", 0, CATCMD_AI },
    { "AM", "Main band to memory channel", 0, CATCMD_AM },
    { "AN", "Antenna number", 0, CATCMD_AN },
    { "AO", "AMC output level", 0, CATCMD_AO },
    { "AV", "Anti VOX level", 0, CATCMD_AV },
    { "BA", "Sub band to main band", 0, CATCMD_BA },
    { "BC", "Auto notch", 0, CATCMD_BC },
    { "BD", "Band down", 0, CATCMD_BD },
    { "BI", "Break-in", 0, CATCMD_BI },
    { "BM", "Sub band to memory channel", 0, CATCMD_BM },
    { "BP", "Manual notch", 0, CATCMD_BP },
    { "BS", "Band select", 0, CATCMD_BS },
    { "BU", "Band up", 0, CATCMD_BU },
    { "BY", "Busy", 0, CATCMD_BY },
    { "CH", "Channel up/down", 0, CATCMD_CH },
    { "CN", "CTCSS/DCS number", 0, CATCMD_CN },
    { "CO", "Contour", 0, CATCMD_CO },
    { "CS", "CW spot", 0, CATCMD_CS },
    { "CT", "CTCSS", 0, CATCMD_CT },
    { "DA", "Dimmer", 0, CATCMD_DA },
    { "DN", "Down", 0, CATCMD_DN },
    { "DT", "Date and time", 0, CATCMD_DT },
    { "ED", "Encoder down", 0, CATCMD_ED },
    { "EM", "Encode memory", 0, CATCMD_EM },
    { "EN", "Encode", 0, CATCMD_EN },
    { "EU", "Encoder up", 0, CATCMD_EU },
    { "EX", "Menu", 0, CATCMD_EX },
    { "FA", "Frequency main band", 9, CATCMD_FA },
    { "FB", "Frequency sub band", 9, CATCMD_FB },
    { "FN", "Fine tuning", 0, CATCMD_FN },
    { "FR", "Function RX", 0, CATCMD_FR },
    { "FS", "Fast step", 0, CATCMD_FS },
    { "FT", "Function TX", 0, CATCMD_FT },
    { "GT", "AGC function", 0, CATCMD_GT },
    { "ID", "Identification", 0, CATCMD_ID },
    { "IF", "Information", 0, CATCMD_IF },
    { "IS", "IF-shift", 0, CATCMD_IS },
    { "KM", "Keyer memory", 0, CATCMD_KM },
    { "KP", "Key pitch", 0, CATCMD_KP },
    { "KR", "Keyer", 0, CATCMD_KR },
    { "KS", "Key speed", 0, CATCMD_KS },
    { "KY", "CW keying", 0, CATCMD_KY },
    { "LK", "Lock", 0, CATCMD_LK },
    { "LM", "Load message", 0, CATCMD_LM },
    { "MA", "Memory channel to main band", 0, CATCMD_MA },
    { "MB", "Memory channel to sub band", 0, CATCMD_MB },
    { "MC", "Memory channel", 0, CATCMD_MC },
    { "MD", "Mode", 0, CATCMD_MD },
    { "MG", "Mic gain", 0, CATCMD_MG },
    { "ML", "Monitor level", 0, CATCMD_ML },
    { "MR", "Memory read", 0, CATCMD_MR },
    { "MS", "Meter switch", 0, CATCMD_MS },
    { "MT", "Memory channel write/tag", 0, CATCMD_MT },
    { "MW", "Memory write", 0, CATCMD_MW },
    { "MX", "MOX set", 0, CATCMD_MX },
    { "NA", "Narrow", 0, CATCMD_NA },
    { "NB", "Noise blanker", 0, CATCMD_NB },
    { "NL", "Noise blanker level", 0, CATCMD_NL },
    { "NR", "Noise reduction", 0, CATCMD_NR },
    { "OI", "Opposite band information", 0, CATCMD_OI },
    { "OS", "Offset (Repeater Shift)", 0, CATCMD_OS },
    { "PA", "Pre-amp (IPO)", 0, CATCMD_PA },
    { "PB", "Play back", 0, CATCMD_PB },
    { "PC", "Power control", 0, CATCMD_PC },
    { "PL", "Speech processor level", 0, CATCMD_PL },
    { "PR", "Speech processor", 0, CATCMD_PR },
    { "PS", "Power switch", 0, CATCMD_PS },
    { "QI", "QMB store", 0, CATCMD_QI },
    { "QR", "QMB recall", 0, CATCMD_QR },
    { "QS", "Quick split", 0, CATCMD_QS },
    { "RA", "RF attenuator", 0, CATCMD_RA },
    { "RC", "Clar clear", 0, CATCMD_RC },
    { "RD", "Clar down", 0, CATCMD_RD },
    { "RF", "Roofing filter", 0, CATCMD_RF },
    { "RG", "RF gain", 0, CATCMD_RG },
    { "RI", "Radio information", 0, CATCMD_RI },
    { "RL", "Noise reduction level", 0, CATCMD_RL },
    { "RM", "Read meter", 0, CATCMD_RM },
    { "RS", "Radio status", 0, CATCMD_RS },
    { "RT", "Clar", 0, CATCMD_RT },
    { "RU", "Clar up", 0, CATCMD_RU },
    { "SC", "Scan", 0, CATCMD_SC },
    { "SD", "Semi break-in delay time", 0, CATCMD_SD },
    { "SF", "Sub dial", 0, CATCMD_SF },
    { "SH", "Width", 0, CATCMD_SH },
    { "SM", "S meter", 0, CATCMD_SM },
    { "SQ", "Squelch level", 0, CATCMD_SQ },
    { "SS", "Spectrum scope", 0, CATCMD_SS },
    { "ST", "Split", 0, CATCMD_ST },
    { "SV", "Swap VFO", 0, CATCMD_SV },
    { "SY", "Sync", 0, CATCMD_SY },
    { "TX", "TX set", 0, CATCMD_TX },
    { "UL", "Unlock", 0, CATCMD_UL },
    { "UP", "Up", 0, CATCMD_UP },
    { "VD", "VOX delay time", 0, CATCMD_VD },
    { "VG", "VOX gain", 0, CATCMD_VG },
    { "VM", "[V/M] key function", 0, CATCMD_VM },
    { "VS", "VFO select", 0, CATCMD_VS },
    { "VT", "VCT(VC tune)", 0, CATCMD_VT },
    { "VX", "VOX", 0, CATCMD_VX },
    { "XT", "TX clar", 0, CATCMD_XT },
    { "ZI", "Zero in", 0, CATCMD_ZI },
};
const size_t catCommandCount = sizeof(catCommands) / sizeof(catCommands[0]);
// Single handler for all commands
void handle_cat_command(CatCommandId id, const char* params);
// To get frequency:
// handle_cat_command(CATCMD_FA, NULL); // or handle_cat_command(CATCMD_FA, "");
// To set frequency to 14.123456 MHz:
// handle_cat_command(CATCMD_FA, "14123456");

// Lookup function: returns pointer to CatCommand, or NULL if not found
const CatCommand* findCatCommand(const char* cmd);

#ifdef __cplusplus
}
#endif

#endif // YAESU_CAT_H
