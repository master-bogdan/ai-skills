# Testing

## Load When

Load when adding, changing, reviewing, or recommending tests.

## Strategy

Testing should be proportional to risk.

- UI: prefer unit and integration tests.
- API: prefer integration and E2E tests.
- Bug fixes should normally have coverage when practical.
- Small low-risk changes do not always need new integration or E2E tests.
- Tests should verify behavior through public interfaces, not implementation
  details.

## Test Naming

Use [file-naming.md](file-naming.md) for required test scope suffixes.

## Blocking

- A high-risk change has no meaningful validation and no explanation.
- Tests assert internal implementation instead of behavior.
- Tests only check plumbing, mocks, or spies while missing observable behavior.
- A bug fix lacks practical coverage and the risk is non-trivial.
- Test names misrepresent scope.

## Advisory

- More coverage would improve confidence but the touched change is low risk.
- Test descriptions could be more behavior-focused.
- A small utility has enough direct unit coverage and does not need broader tests.

## Examples

Good UI behavior test:

```tsx
it('submits import form and shows success state', async () => {
  render(<CreateImportModal />);
  await user.selectOptions(screen.getByLabelText(/sheet/i), 'Summary');
  await user.click(screen.getByRole('button', { name: /submit/i }));

  expect(await screen.findByText(/import created/i)).toBeInTheDocument();
});
```

Bad shallow UI test:

```tsx
it('renders button', () => {
  render(<CreateImportModal />);
  expect(screen.getByRole('button')).toBeInTheDocument();
});
```

Good API E2E boundary test:

```ts
describe('POST /imports', () => {
  it('creates import job for valid request', async () => {
    const response = await request(app)
      .post('/imports')
      .send({ sheetId: 'sheet-1' })
      .expect(201);

    expect(response.body.status).toBe(IMPORT_STATUS.PENDING);
  });
});
```

Bad implementation test:

```ts
it('calls repository', async () => {
  const spy = vi.spyOn(repository, 'createImportRepository');
  await createImportService({ input: { sheetId: 'sheet-1' }, userId: 'user-1' });
  expect(spy).toHaveBeenCalled();
});
```
