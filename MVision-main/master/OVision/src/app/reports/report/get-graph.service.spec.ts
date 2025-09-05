import { TestBed } from '@angular/core/testing';

import { GetGraphService } from './get-graph.service';

describe('GetGraphService', () => {
  let service: GetGraphService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetGraphService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
