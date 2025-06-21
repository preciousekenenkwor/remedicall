/* eslint-disable @typescript-eslint/no-explicit-any */
const clearTable = async (table: string) => {
  const t = window.CACHE[table];
  if (!t) return;

  await t.iterate((_data: any, key: any) => {
    t.removeItem(key);
  });
};

export default clearTable;
