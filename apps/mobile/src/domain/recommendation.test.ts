import { describe, expect, it } from 'vitest';

import { validateSearchInput } from './recommendation';

describe('validateSearchInput', () => {
  it('normalizes a valid query and budget', () => {
    expect(validateSearchInput(' 회사 워크숍에 입을 셔츠 ', '150,000원')).toEqual({
      ok: true,
      query: '회사 워크숍에 입을 셔츠',
      budget: 150000,
    });
  });

  it('rejects a short query', () => {
    expect(validateSearchInput('셔츠', '150000')).toMatchObject({ ok: false });
  });

  it('rejects an unreasonable budget', () => {
    expect(validateSearchInput('회사 워크숍 셔츠', '5000')).toMatchObject({ ok: false });
  });
});
